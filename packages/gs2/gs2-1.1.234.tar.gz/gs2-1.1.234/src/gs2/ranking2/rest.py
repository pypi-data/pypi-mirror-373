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


class Gs2Ranking2RestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
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
            service='ranking2',
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
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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
            service='ranking2',
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

    def _describe_global_ranking_models(
        self,
        request: DescribeGlobalRankingModelsRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/global".format(
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
            result_type=DescribeGlobalRankingModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetGlobalRankingModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/global".format(
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
            result_type=DescribeGlobalRankingModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/global".format(
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateGlobalRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetGlobalRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateGlobalRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=DeleteGlobalRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/global".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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
            result_type=DescribeGlobalRankingScoresResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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
            result_type=DescribeGlobalRankingScoresByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutGlobalRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutGlobalRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingScoreResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global/{rankingName}/{season}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteGlobalRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global/{rankingName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifyGlobalRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/global/{rankingName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifyGlobalRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/stamp/global/score/verify"

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
            result_type=VerifyGlobalRankingScoreByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/global/reward/received".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeGlobalRankingReceivedRewardsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/global/reward/received".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeGlobalRankingReceivedRewardsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/global/reward/received/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateGlobalRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/global/reward/received/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateGlobalRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/global/reward/received/{rankingName}/{season}/reward/receive".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            season=request.season if request.season is not None and request.season != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
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
            result_type=ReceiveGlobalRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/global/reward/received/{rankingName}/{season}/reward/receive".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            season=request.season if request.season is not None and request.season != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
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
            result_type=ReceiveGlobalRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/global/reward/received/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/global/reward/received/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/global/reward/received/{rankingName}/{season}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteGlobalRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/stamp/ranking/global/reward/receive"

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
            result_type=CreateGlobalRankingReceivedRewardByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/global/{rankingName}/user/me".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeGlobalRankingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/global/{rankingName}/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeGlobalRankingsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/global/{rankingName}/user/me/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/global/{rankingName}/user/{userId}/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetGlobalRankingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/cluster".format(
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
            result_type=DescribeClusterRankingModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/cluster/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetClusterRankingModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/cluster".format(
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
            result_type=DescribeClusterRankingModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/cluster".format(
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateClusterRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/cluster/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetClusterRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/cluster/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateClusterRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/cluster/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=DeleteClusterRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/cluster".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            query_strings["clusterName"] = request.cluster_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingScoresResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            query_strings["clusterName"] = request.cluster_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingScoresByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/cluster/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutClusterRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutClusterRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/cluster/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingScoreResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster/{rankingName}/{clusterName}/{season}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteClusterRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster/{rankingName}/{clusterName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifyClusterRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/cluster/{rankingName}/{clusterName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifyClusterRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/stamp/cluster/score/verify"

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
            result_type=VerifyClusterRankingScoreByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/cluster/reward/received".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            query_strings["clusterName"] = request.cluster_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingReceivedRewardsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/cluster/reward/received".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            query_strings["clusterName"] = request.cluster_name
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingReceivedRewardsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/cluster/reward/received/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateClusterRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/cluster/reward/received/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateClusterRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/cluster/reward/received/{rankingName}/{clusterName}/{season}/reward/receive".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            season=request.season if request.season is not None and request.season != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
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
            result_type=ReceiveClusterRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/cluster/reward/received/{rankingName}/{clusterName}/{season}/reward/receive".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            season=request.season if request.season is not None and request.season != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
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
            result_type=ReceiveClusterRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/cluster/reward/received/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingReceivedRewardResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/cluster/reward/received/{rankingName}/{clusterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/cluster/reward/received/{rankingName}/{clusterName}/{season}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteClusterRankingReceivedRewardByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/stamp/ranking/cluster/reward/receive"

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
            result_type=CreateClusterRankingReceivedRewardByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/cluster/{rankingName}/{clusterName}/user/me".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/cluster/{rankingName}/{clusterName}/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeClusterRankingsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/cluster/{rankingName}/{clusterName}/user/me/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/cluster/{rankingName}/{clusterName}/user/{userId}/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            clusterName=request.cluster_name if request.cluster_name is not None and request.cluster_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetClusterRankingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/subscribe".format(
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
            result_type=DescribeSubscribeRankingModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/model/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetSubscribeRankingModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/subscribe".format(
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
            result_type=DescribeSubscribeRankingModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/subscribe".format(
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateSubscribeRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=GetSubscribeRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateSubscribeRankingModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/master/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
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
            result_type=DeleteSubscribeRankingModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/score".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/score".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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

    def _add_subscribe(
        self,
        request: AddSubscribeRequest,
        callback: Callable[[AsyncResult[AddSubscribeResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            method='PUT',
            result_type=AddSubscribeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            method='PUT',
            result_type=AddSubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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
            result_type=DescribeSubscribeRankingScoresResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.ranking_name is not None:
            query_strings["rankingName"] = request.ranking_name
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
            result_type=DescribeSubscribeRankingScoresByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutSubscribeRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PutSubscribeRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/score/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeRankingScoreResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe/{rankingName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe/{rankingName}/{season}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteSubscribeRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe/{rankingName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifySubscribeRankingScoreResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/score/subscribe/{rankingName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
            result_type=VerifySubscribeRankingScoreByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/stamp/subscribe/score/verify"

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
            result_type=VerifySubscribeRankingScoreByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/subscribe/{rankingName}/user/me".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeSubscribeRankingsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/subscribe/{rankingName}/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
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
            result_type=DescribeSubscribeRankingsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/subscribe/{rankingName}/user/me/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
        if request.scorer_user_id is not None:
            query_strings["scorerUserId"] = request.scorer_user_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeRankingResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/ranking/subscribe/{rankingName}/user/{userId}/rank".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.season is not None:
            query_strings["season"] = request.season
        if request.scorer_user_id is not None:
            query_strings["scorerUserId"] = request.scorer_user_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeRankingByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            service='ranking2',
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

    def _get_current_ranking_master(
        self,
        request: GetCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentRankingMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
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
            result_type=GetCurrentRankingMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
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
            result_type=PreUpdateCurrentRankingMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_ranking_master(
                PreUpdateCurrentRankingMasterRequest() \
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
            service='ranking2',
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
            result_type=UpdateCurrentRankingMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
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
            result_type=UpdateCurrentRankingMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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

    def _delete_subscribe(
        self,
        request: DeleteSubscribeRequest,
        callback: Callable[[AsyncResult[DeleteSubscribeResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=DeleteSubscribeResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='ranking2',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/subscribe/{rankingName}/target/{targetUserId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            rankingName=request.ranking_name if request.ranking_name is not None and request.ranking_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            targetUserId=request.target_user_id if request.target_user_id is not None and request.target_user_id != '' else 'null',
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
            result_type=DeleteSubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result