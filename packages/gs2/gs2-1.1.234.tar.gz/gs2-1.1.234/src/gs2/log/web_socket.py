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


class Gs2LogWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
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
            service="log",
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
            service="log",
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
            service="log",
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
            service="log",
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
            service="log",
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
            service="log",
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

    def _query_access_log(
        self,
        request: QueryAccessLogRequest,
        callback: Callable[[AsyncResult[QueryAccessLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='accessLog',
            function='queryAccessLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryAccessLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='accessLog',
            function='countAccessLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CountAccessLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='issueStampSheetLog',
            function='queryIssueStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryIssueStampSheetLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='issueStampSheetLog',
            function='countIssueStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CountIssueStampSheetLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampSheetLog',
            function='queryExecuteStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryExecuteStampSheetLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampSheetLog',
            function='countExecuteStampSheetLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CountExecuteStampSheetLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampTaskLog',
            function='queryExecuteStampTaskLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryExecuteStampTaskLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='executeStampTaskLog',
            function='countExecuteStampTaskLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.service is not None:
            body["service"] = request.service
        if request.method is not None:
            body["method"] = request.method
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.action is not None:
            body["action"] = request.action
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CountExecuteStampTaskLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='inGameLog',
            function='queryInGameLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryInGameLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='inGameLog',
            function='sendInGameLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.tags is not None:
            body["tags"] = [
                item.to_dict()
                for item in request.tags
            ]
        if request.payload is not None:
            body["payload"] = request.payload

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SendInGameLogResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='inGameLog',
            function='sendInGameLogByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.tags is not None:
            body["tags"] = [
                item.to_dict()
                for item in request.tags
            ]
        if request.payload is not None:
            body["payload"] = request.payload
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SendInGameLogByUserIdResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='accessLogWithTelemetry',
            function='queryAccessLogWithTelemetry',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
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
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=QueryAccessLogWithTelemetryResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='insight',
            function='describeInsights',
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
                result_type=DescribeInsightsResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='insight',
            function='createInsight',
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
                result_type=CreateInsightResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='insight',
            function='getInsight',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.insight_name is not None:
            body["insightName"] = request.insight_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetInsightResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="log",
            component='insight',
            function='deleteInsight',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.insight_name is not None:
            body["insightName"] = request.insight_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteInsightResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result