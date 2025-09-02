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


class Gs2EnchantRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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
            service='enchant',
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

    def _describe_balance_parameter_models(
        self,
        request: DescribeBalanceParameterModelsRequest,
        callback: Callable[[AsyncResult[DescribeBalanceParameterModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/model/balance".format(
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
            result_type=DescribeBalanceParameterModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/model/balance/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=GetBalanceParameterModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/balance".format(
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
            result_type=DescribeBalanceParameterModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/balance".format(
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateBalanceParameterModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/balance/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=GetBalanceParameterModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/balance/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateBalanceParameterModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/balance/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=DeleteBalanceParameterModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/model/rarity".format(
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
            result_type=DescribeRarityParameterModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/model/rarity/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=GetRarityParameterModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/rarity".format(
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
            result_type=DescribeRarityParameterModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/rarity".format(
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRarityParameterModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/rarity/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=GetRarityParameterModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/rarity/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRarityParameterModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/rarity/{parameterName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
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
            result_type=DeleteRarityParameterModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            service='enchant',
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

    def _get_current_parameter_master(
        self,
        request: GetCurrentParameterMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentParameterMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
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
            result_type=GetCurrentParameterMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
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
            result_type=PreUpdateCurrentParameterMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_parameter_master(
                PreUpdateCurrentParameterMasterRequest() \
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
            service='enchant',
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
            result_type=UpdateCurrentParameterMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
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
            result_type=UpdateCurrentParameterMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/status/balance".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.parameter_name is not None:
            query_strings["parameterName"] = request.parameter_name
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
            result_type=DescribeBalanceParameterStatusesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/balance".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.parameter_name is not None:
            query_strings["parameterName"] = request.parameter_name
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
            result_type=DescribeBalanceParameterStatusesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/status/balance/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=GetBalanceParameterStatusResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/balance/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=GetBalanceParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/balance/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=DeleteBalanceParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/balance/{parameterName}/{propertyId}/redraw".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.fixed_parameter_names is not None:
            body["fixedParameterNames"] = [
                item
                for item in request.fixed_parameter_names
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
            result_type=ReDrawBalanceParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/balance/redraw"

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
            result_type=ReDrawBalanceParameterStatusByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/balance/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.parameter_values is not None:
            body["parameterValues"] = [
                item.to_dict()
                for item in request.parameter_values
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
            result_type=SetBalanceParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/balance/set"

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
            result_type=SetBalanceParameterStatusByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/status/rarity".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.parameter_name is not None:
            query_strings["parameterName"] = request.parameter_name
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
            result_type=DescribeRarityParameterStatusesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.parameter_name is not None:
            query_strings["parameterName"] = request.parameter_name
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
            result_type=DescribeRarityParameterStatusesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/status/rarity/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=GetRarityParameterStatusResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=GetRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            result_type=DeleteRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}/redraw".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.fixed_parameter_names is not None:
            body["fixedParameterNames"] = [
                item
                for item in request.fixed_parameter_names
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
            result_type=ReDrawRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/rarity/parameter/redraw"

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
            result_type=ReDrawRarityParameterStatusByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}/add".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
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
            method='POST',
            result_type=AddRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/rarity/parameter/add"

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
            result_type=AddRarityParameterStatusByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/status/rarity/{parameterName}/{propertyId}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.parameter_value_name is not None:
            body["parameterValueName"] = request.parameter_value_name
        if request.parameter_count is not None:
            body["parameterCount"] = request.parameter_count
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
            result_type=VerifyRarityParameterStatusResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.parameter_value_name is not None:
            body["parameterValueName"] = request.parameter_value_name
        if request.parameter_count is not None:
            body["parameterCount"] = request.parameter_count
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
            result_type=VerifyRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/rarity/parameter/verify"

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
            result_type=VerifyRarityParameterStatusByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/status/rarity/{parameterName}/{propertyId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            parameterName=request.parameter_name if request.parameter_name is not None and request.parameter_name != '' else 'null',
            propertyId=request.property_id if request.property_id is not None and request.property_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.parameter_values is not None:
            body["parameterValues"] = [
                item.to_dict()
                for item in request.parameter_values
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
            result_type=SetRarityParameterStatusByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='enchant',
            region=self.session.region,
        ) + "/stamp/rarity/parameter/set"

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
            result_type=SetRarityParameterStatusByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result