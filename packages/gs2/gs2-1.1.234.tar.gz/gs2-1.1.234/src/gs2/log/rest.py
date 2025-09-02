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


class Gs2LogRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
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
            service='log',
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
        if request.type is not None:
            body["type"] = request.type
        if request.gcp_credential_json is not None:
            body["gcpCredentialJson"] = request.gcp_credential_json
        if request.big_query_dataset_name is not None:
            body["bigQueryDatasetName"] = request.big_query_dataset_name
        if request.log_expire_days is not None:
            body["logExpireDays"] = request.log_expire_days
        if request.aws_region is not None:
            body["awsRegion"] = request.aws_region
        if request.aws_access_key_id is not None:
            body["awsAccessKeyId"] = request.aws_access_key_id
        if request.aws_secret_access_key is not None:
            body["awsSecretAccessKey"] = request.aws_secret_access_key
        if request.firehose_stream_name is not None:
            body["firehoseStreamName"] = request.firehose_stream_name
        if request.firehose_compress_data is not None:
            body["firehoseCompressData"] = request.firehose_compress_data

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
            service='log',
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
            service='log',
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
            service='log',
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
        if request.type is not None:
            body["type"] = request.type
        if request.gcp_credential_json is not None:
            body["gcpCredentialJson"] = request.gcp_credential_json
        if request.big_query_dataset_name is not None:
            body["bigQueryDatasetName"] = request.big_query_dataset_name
        if request.log_expire_days is not None:
            body["logExpireDays"] = request.log_expire_days
        if request.aws_region is not None:
            body["awsRegion"] = request.aws_region
        if request.aws_access_key_id is not None:
            body["awsAccessKeyId"] = request.aws_access_key_id
        if request.aws_secret_access_key is not None:
            body["awsSecretAccessKey"] = request.aws_secret_access_key
        if request.firehose_stream_name is not None:
            body["firehoseStreamName"] = request.firehose_stream_name
        if request.firehose_compress_data is not None:
            body["firehoseCompressData"] = request.firehose_compress_data

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
            service='log',
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
            service='log',
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

    def _query_access_log(
        self,
        request: QueryAccessLogRequest,
        callback: Callable[[AsyncResult[QueryAccessLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/access".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=QueryAccessLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_access_log(
        self,
        request: QueryAccessLogRequest,
    ) -> QueryAccessLogResult:
        async_result = []
        with timeout(30):
            self._query_access_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_access_log_async(
        self,
        request: QueryAccessLogRequest,
    ) -> QueryAccessLogResult:
        async_result = []
        self._query_access_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _count_access_log(
        self,
        request: CountAccessLogRequest,
        callback: Callable[[AsyncResult[CountAccessLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/access/count".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=CountAccessLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def count_access_log(
        self,
        request: CountAccessLogRequest,
    ) -> CountAccessLogResult:
        async_result = []
        with timeout(30):
            self._count_access_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_access_log_async(
        self,
        request: CountAccessLogRequest,
    ) -> CountAccessLogResult:
        async_result = []
        self._count_access_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _query_issue_stamp_sheet_log(
        self,
        request: QueryIssueStampSheetLogRequest,
        callback: Callable[[AsyncResult[QueryIssueStampSheetLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/issue/stamp/sheet".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=QueryIssueStampSheetLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_issue_stamp_sheet_log(
        self,
        request: QueryIssueStampSheetLogRequest,
    ) -> QueryIssueStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._query_issue_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_issue_stamp_sheet_log_async(
        self,
        request: QueryIssueStampSheetLogRequest,
    ) -> QueryIssueStampSheetLogResult:
        async_result = []
        self._query_issue_stamp_sheet_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _count_issue_stamp_sheet_log(
        self,
        request: CountIssueStampSheetLogRequest,
        callback: Callable[[AsyncResult[CountIssueStampSheetLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/issue/stamp/sheet/count".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=CountIssueStampSheetLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def count_issue_stamp_sheet_log(
        self,
        request: CountIssueStampSheetLogRequest,
    ) -> CountIssueStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._count_issue_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_issue_stamp_sheet_log_async(
        self,
        request: CountIssueStampSheetLogRequest,
    ) -> CountIssueStampSheetLogResult:
        async_result = []
        self._count_issue_stamp_sheet_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _query_execute_stamp_sheet_log(
        self,
        request: QueryExecuteStampSheetLogRequest,
        callback: Callable[[AsyncResult[QueryExecuteStampSheetLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/execute/stamp/sheet".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=QueryExecuteStampSheetLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_execute_stamp_sheet_log(
        self,
        request: QueryExecuteStampSheetLogRequest,
    ) -> QueryExecuteStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._query_execute_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_execute_stamp_sheet_log_async(
        self,
        request: QueryExecuteStampSheetLogRequest,
    ) -> QueryExecuteStampSheetLogResult:
        async_result = []
        self._query_execute_stamp_sheet_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _count_execute_stamp_sheet_log(
        self,
        request: CountExecuteStampSheetLogRequest,
        callback: Callable[[AsyncResult[CountExecuteStampSheetLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/execute/stamp/sheet/count".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=CountExecuteStampSheetLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def count_execute_stamp_sheet_log(
        self,
        request: CountExecuteStampSheetLogRequest,
    ) -> CountExecuteStampSheetLogResult:
        async_result = []
        with timeout(30):
            self._count_execute_stamp_sheet_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_execute_stamp_sheet_log_async(
        self,
        request: CountExecuteStampSheetLogRequest,
    ) -> CountExecuteStampSheetLogResult:
        async_result = []
        self._count_execute_stamp_sheet_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _query_execute_stamp_task_log(
        self,
        request: QueryExecuteStampTaskLogRequest,
        callback: Callable[[AsyncResult[QueryExecuteStampTaskLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/execute/stamp/task".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=QueryExecuteStampTaskLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_execute_stamp_task_log(
        self,
        request: QueryExecuteStampTaskLogRequest,
    ) -> QueryExecuteStampTaskLogResult:
        async_result = []
        with timeout(30):
            self._query_execute_stamp_task_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_execute_stamp_task_log_async(
        self,
        request: QueryExecuteStampTaskLogRequest,
    ) -> QueryExecuteStampTaskLogResult:
        async_result = []
        self._query_execute_stamp_task_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _count_execute_stamp_task_log(
        self,
        request: CountExecuteStampTaskLogRequest,
        callback: Callable[[AsyncResult[CountExecuteStampTaskLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/execute/stamp/task/count".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.service is not None:
            query_strings["service"] = request.service
        if request.method is not None:
            query_strings["method"] = request.method
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.action is not None:
            query_strings["action"] = request.action
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=CountExecuteStampTaskLogResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def count_execute_stamp_task_log(
        self,
        request: CountExecuteStampTaskLogRequest,
    ) -> CountExecuteStampTaskLogResult:
        async_result = []
        with timeout(30):
            self._count_execute_stamp_task_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def count_execute_stamp_task_log_async(
        self,
        request: CountExecuteStampTaskLogRequest,
    ) -> CountExecuteStampTaskLogResult:
        async_result = []
        self._count_execute_stamp_task_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _query_in_game_log(
        self,
        request: QueryInGameLogRequest,
        callback: Callable[[AsyncResult[QueryInGameLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/ingame/log".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.tags is not None:
            body["tags"] = [
                item.to_dict()
                for item in request.tags
            ]
        if request.begin is not None:
            body["begin"] = request.begin
        if request.end is not None:
            body["end"] = request.end
        if request.long_term is not None:
            body["longTerm"] = request.long_term
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=QueryInGameLogResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_in_game_log(
        self,
        request: QueryInGameLogRequest,
    ) -> QueryInGameLogResult:
        async_result = []
        with timeout(30):
            self._query_in_game_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_in_game_log_async(
        self,
        request: QueryInGameLogRequest,
    ) -> QueryInGameLogResult:
        async_result = []
        self._query_in_game_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _send_in_game_log(
        self,
        request: SendInGameLogRequest,
        callback: Callable[[AsyncResult[SendInGameLogResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/ingame/log/user/me/send".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.tags is not None:
            body["tags"] = [
                item.to_dict()
                for item in request.tags
            ]
        if request.payload is not None:
            body["payload"] = request.payload

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SendInGameLogResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def send_in_game_log(
        self,
        request: SendInGameLogRequest,
    ) -> SendInGameLogResult:
        async_result = []
        with timeout(30):
            self._send_in_game_log(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def send_in_game_log_async(
        self,
        request: SendInGameLogRequest,
    ) -> SendInGameLogResult:
        async_result = []
        self._send_in_game_log(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _send_in_game_log_by_user_id(
        self,
        request: SendInGameLogByUserIdRequest,
        callback: Callable[[AsyncResult[SendInGameLogByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/ingame/log/user/{userId}/send".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.tags is not None:
            body["tags"] = [
                item.to_dict()
                for item in request.tags
            ]
        if request.payload is not None:
            body["payload"] = request.payload

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SendInGameLogByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def send_in_game_log_by_user_id(
        self,
        request: SendInGameLogByUserIdRequest,
    ) -> SendInGameLogByUserIdResult:
        async_result = []
        with timeout(30):
            self._send_in_game_log_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def send_in_game_log_by_user_id_async(
        self,
        request: SendInGameLogByUserIdRequest,
    ) -> SendInGameLogByUserIdResult:
        async_result = []
        self._send_in_game_log_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _query_access_log_with_telemetry(
        self,
        request: QueryAccessLogWithTelemetryRequest,
        callback: Callable[[AsyncResult[QueryAccessLogWithTelemetryResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/log/access/telemetry".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.begin is not None:
            query_strings["begin"] = request.begin
        if request.end is not None:
            query_strings["end"] = request.end
        if request.long_term is not None:
            query_strings["longTerm"] = request.long_term
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
            result_type=QueryAccessLogWithTelemetryResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def query_access_log_with_telemetry(
        self,
        request: QueryAccessLogWithTelemetryRequest,
    ) -> QueryAccessLogWithTelemetryResult:
        async_result = []
        with timeout(30):
            self._query_access_log_with_telemetry(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def query_access_log_with_telemetry_async(
        self,
        request: QueryAccessLogWithTelemetryRequest,
    ) -> QueryAccessLogWithTelemetryResult:
        async_result = []
        self._query_access_log_with_telemetry(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_insights(
        self,
        request: DescribeInsightsRequest,
        callback: Callable[[AsyncResult[DescribeInsightsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/insight".format(
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
            result_type=DescribeInsightsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_insights(
        self,
        request: DescribeInsightsRequest,
    ) -> DescribeInsightsResult:
        async_result = []
        with timeout(30):
            self._describe_insights(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_insights_async(
        self,
        request: DescribeInsightsRequest,
    ) -> DescribeInsightsResult:
        async_result = []
        self._describe_insights(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_insight(
        self,
        request: CreateInsightRequest,
        callback: Callable[[AsyncResult[CreateInsightResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/insight".format(
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
            result_type=CreateInsightResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_insight(
        self,
        request: CreateInsightRequest,
    ) -> CreateInsightResult:
        async_result = []
        with timeout(30):
            self._create_insight(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_insight_async(
        self,
        request: CreateInsightRequest,
    ) -> CreateInsightResult:
        async_result = []
        self._create_insight(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_insight(
        self,
        request: GetInsightRequest,
        callback: Callable[[AsyncResult[GetInsightResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/insight/{insightName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            insightName=request.insight_name if request.insight_name is not None and request.insight_name != '' else 'null',
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
            result_type=GetInsightResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_insight(
        self,
        request: GetInsightRequest,
    ) -> GetInsightResult:
        async_result = []
        with timeout(30):
            self._get_insight(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_insight_async(
        self,
        request: GetInsightRequest,
    ) -> GetInsightResult:
        async_result = []
        self._get_insight(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_insight(
        self,
        request: DeleteInsightRequest,
        callback: Callable[[AsyncResult[DeleteInsightResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='log',
            region=self.session.region,
        ) + "/{namespaceName}/insight/{insightName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            insightName=request.insight_name if request.insight_name is not None and request.insight_name != '' else 'null',
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
            result_type=DeleteInsightResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_insight(
        self,
        request: DeleteInsightRequest,
    ) -> DeleteInsightResult:
        async_result = []
        with timeout(30):
            self._delete_insight(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_insight_async(
        self,
        request: DeleteInsightRequest,
    ) -> DeleteInsightResult:
        async_result = []
        self._delete_insight(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result