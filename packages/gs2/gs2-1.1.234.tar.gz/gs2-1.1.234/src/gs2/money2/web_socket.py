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


class Gs2Money2WebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
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
            service="money2",
            component='namespace',
            function='createNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.currency_usage_priority is not None:
            body["currencyUsagePriority"] = request.currency_usage_priority
        if request.description is not None:
            body["description"] = request.description
        if request.shared_free_currency is not None:
            body["sharedFreeCurrency"] = request.shared_free_currency
        if request.platform_setting is not None:
            body["platformSetting"] = request.platform_setting.to_dict()
        if request.deposit_balance_script is not None:
            body["depositBalanceScript"] = request.deposit_balance_script.to_dict()
        if request.withdraw_balance_script is not None:
            body["withdrawBalanceScript"] = request.withdraw_balance_script.to_dict()
        if request.verify_receipt_script is not None:
            body["verifyReceiptScript"] = request.verify_receipt_script.to_dict()
        if request.subscribe_script is not None:
            body["subscribeScript"] = request.subscribe_script
        if request.renew_script is not None:
            body["renewScript"] = request.renew_script
        if request.unsubscribe_script is not None:
            body["unsubscribeScript"] = request.unsubscribe_script
        if request.take_over_script is not None:
            body["takeOverScript"] = request.take_over_script.to_dict()
        if request.change_subscription_status_notification is not None:
            body["changeSubscriptionStatusNotification"] = request.change_subscription_status_notification.to_dict()
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
            service="money2",
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
            service="money2",
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
            service="money2",
            component='namespace',
            function='updateNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.currency_usage_priority is not None:
            body["currencyUsagePriority"] = request.currency_usage_priority
        if request.description is not None:
            body["description"] = request.description
        if request.platform_setting is not None:
            body["platformSetting"] = request.platform_setting.to_dict()
        if request.deposit_balance_script is not None:
            body["depositBalanceScript"] = request.deposit_balance_script.to_dict()
        if request.withdraw_balance_script is not None:
            body["withdrawBalanceScript"] = request.withdraw_balance_script.to_dict()
        if request.verify_receipt_script is not None:
            body["verifyReceiptScript"] = request.verify_receipt_script.to_dict()
        if request.subscribe_script is not None:
            body["subscribeScript"] = request.subscribe_script
        if request.renew_script is not None:
            body["renewScript"] = request.renew_script
        if request.unsubscribe_script is not None:
            body["unsubscribeScript"] = request.unsubscribe_script
        if request.take_over_script is not None:
            body["takeOverScript"] = request.take_over_script.to_dict()
        if request.change_subscription_status_notification is not None:
            body["changeSubscriptionStatusNotification"] = request.change_subscription_status_notification.to_dict()
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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

    def _describe_wallets(
        self,
        request: DescribeWalletsRequest,
        callback: Callable[[AsyncResult[DescribeWalletsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='describeWallets',
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
                result_type=DescribeWalletsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_wallets(
        self,
        request: DescribeWalletsRequest,
    ) -> DescribeWalletsResult:
        async_result = []
        with timeout(30):
            self._describe_wallets(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_wallets_async(
        self,
        request: DescribeWalletsRequest,
    ) -> DescribeWalletsResult:
        async_result = []
        self._describe_wallets(
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

    def _describe_wallets_by_user_id(
        self,
        request: DescribeWalletsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeWalletsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='describeWalletsByUserId',
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
                result_type=DescribeWalletsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_wallets_by_user_id(
        self,
        request: DescribeWalletsByUserIdRequest,
    ) -> DescribeWalletsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_wallets_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_wallets_by_user_id_async(
        self,
        request: DescribeWalletsByUserIdRequest,
    ) -> DescribeWalletsByUserIdResult:
        async_result = []
        self._describe_wallets_by_user_id(
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

    def _get_wallet(
        self,
        request: GetWalletRequest,
        callback: Callable[[AsyncResult[GetWalletResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='getWallet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.slot is not None:
            body["slot"] = request.slot

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetWalletResult,
                callback=callback,
                body=body,
            )
        )

    def get_wallet(
        self,
        request: GetWalletRequest,
    ) -> GetWalletResult:
        async_result = []
        with timeout(30):
            self._get_wallet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_wallet_async(
        self,
        request: GetWalletRequest,
    ) -> GetWalletResult:
        async_result = []
        self._get_wallet(
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

    def _get_wallet_by_user_id(
        self,
        request: GetWalletByUserIdRequest,
        callback: Callable[[AsyncResult[GetWalletByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='getWalletByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.slot is not None:
            body["slot"] = request.slot
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetWalletByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_wallet_by_user_id(
        self,
        request: GetWalletByUserIdRequest,
    ) -> GetWalletByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_wallet_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_wallet_by_user_id_async(
        self,
        request: GetWalletByUserIdRequest,
    ) -> GetWalletByUserIdResult:
        async_result = []
        self._get_wallet_by_user_id(
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

    def _deposit_by_user_id(
        self,
        request: DepositByUserIdRequest,
        callback: Callable[[AsyncResult[DepositByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='depositByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.slot is not None:
            body["slot"] = request.slot
        if request.deposit_transactions is not None:
            body["depositTransactions"] = [
                item.to_dict()
                for item in request.deposit_transactions
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
                result_type=DepositByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def deposit_by_user_id(
        self,
        request: DepositByUserIdRequest,
    ) -> DepositByUserIdResult:
        async_result = []
        with timeout(30):
            self._deposit_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def deposit_by_user_id_async(
        self,
        request: DepositByUserIdRequest,
    ) -> DepositByUserIdResult:
        async_result = []
        self._deposit_by_user_id(
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

    def _withdraw(
        self,
        request: WithdrawRequest,
        callback: Callable[[AsyncResult[WithdrawResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='withdraw',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.slot is not None:
            body["slot"] = request.slot
        if request.withdraw_count is not None:
            body["withdrawCount"] = request.withdraw_count
        if request.paid_only is not None:
            body["paidOnly"] = request.paid_only

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WithdrawResult,
                callback=callback,
                body=body,
            )
        )

    def withdraw(
        self,
        request: WithdrawRequest,
    ) -> WithdrawResult:
        async_result = []
        with timeout(30):
            self._withdraw(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def withdraw_async(
        self,
        request: WithdrawRequest,
    ) -> WithdrawResult:
        async_result = []
        self._withdraw(
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

    def _withdraw_by_user_id(
        self,
        request: WithdrawByUserIdRequest,
        callback: Callable[[AsyncResult[WithdrawByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='withdrawByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.slot is not None:
            body["slot"] = request.slot
        if request.withdraw_count is not None:
            body["withdrawCount"] = request.withdraw_count
        if request.paid_only is not None:
            body["paidOnly"] = request.paid_only
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WithdrawByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def withdraw_by_user_id(
        self,
        request: WithdrawByUserIdRequest,
    ) -> WithdrawByUserIdResult:
        async_result = []
        with timeout(30):
            self._withdraw_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def withdraw_by_user_id_async(
        self,
        request: WithdrawByUserIdRequest,
    ) -> WithdrawByUserIdResult:
        async_result = []
        self._withdraw_by_user_id(
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

    def _deposit_by_stamp_sheet(
        self,
        request: DepositByStampSheetRequest,
        callback: Callable[[AsyncResult[DepositByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='depositByStampSheet',
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
                result_type=DepositByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def deposit_by_stamp_sheet(
        self,
        request: DepositByStampSheetRequest,
    ) -> DepositByStampSheetResult:
        async_result = []
        with timeout(30):
            self._deposit_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def deposit_by_stamp_sheet_async(
        self,
        request: DepositByStampSheetRequest,
    ) -> DepositByStampSheetResult:
        async_result = []
        self._deposit_by_stamp_sheet(
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

    def _withdraw_by_stamp_task(
        self,
        request: WithdrawByStampTaskRequest,
        callback: Callable[[AsyncResult[WithdrawByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='wallet',
            function='withdrawByStampTask',
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
                result_type=WithdrawByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def withdraw_by_stamp_task(
        self,
        request: WithdrawByStampTaskRequest,
    ) -> WithdrawByStampTaskResult:
        async_result = []
        with timeout(30):
            self._withdraw_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def withdraw_by_stamp_task_async(
        self,
        request: WithdrawByStampTaskRequest,
    ) -> WithdrawByStampTaskResult:
        async_result = []
        self._withdraw_by_stamp_task(
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

    def _describe_events_by_user_id(
        self,
        request: DescribeEventsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeEventsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='event',
            function='describeEventsByUserId',
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
                result_type=DescribeEventsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_events_by_user_id(
        self,
        request: DescribeEventsByUserIdRequest,
    ) -> DescribeEventsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_events_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_events_by_user_id_async(
        self,
        request: DescribeEventsByUserIdRequest,
    ) -> DescribeEventsByUserIdResult:
        async_result = []
        self._describe_events_by_user_id(
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

    def _get_event_by_transaction_id(
        self,
        request: GetEventByTransactionIdRequest,
        callback: Callable[[AsyncResult[GetEventByTransactionIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='event',
            function='getEventByTransactionId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetEventByTransactionIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_event_by_transaction_id(
        self,
        request: GetEventByTransactionIdRequest,
    ) -> GetEventByTransactionIdResult:
        async_result = []
        with timeout(30):
            self._get_event_by_transaction_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_event_by_transaction_id_async(
        self,
        request: GetEventByTransactionIdRequest,
    ) -> GetEventByTransactionIdResult:
        async_result = []
        self._get_event_by_transaction_id(
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

    def _verify_receipt(
        self,
        request: VerifyReceiptRequest,
        callback: Callable[[AsyncResult[VerifyReceiptResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='event',
            function='verifyReceipt',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.content_name is not None:
            body["contentName"] = request.content_name
        if request.receipt is not None:
            body["receipt"] = request.receipt.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyReceiptResult,
                callback=callback,
                body=body,
            )
        )

    def verify_receipt(
        self,
        request: VerifyReceiptRequest,
    ) -> VerifyReceiptResult:
        async_result = []
        with timeout(30):
            self._verify_receipt(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_receipt_async(
        self,
        request: VerifyReceiptRequest,
    ) -> VerifyReceiptResult:
        async_result = []
        self._verify_receipt(
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

    def _verify_receipt_by_user_id(
        self,
        request: VerifyReceiptByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyReceiptByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='event',
            function='verifyReceiptByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.content_name is not None:
            body["contentName"] = request.content_name
        if request.receipt is not None:
            body["receipt"] = request.receipt.to_dict()
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyReceiptByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_receipt_by_user_id(
        self,
        request: VerifyReceiptByUserIdRequest,
    ) -> VerifyReceiptByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_receipt_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_receipt_by_user_id_async(
        self,
        request: VerifyReceiptByUserIdRequest,
    ) -> VerifyReceiptByUserIdResult:
        async_result = []
        self._verify_receipt_by_user_id(
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

    def _verify_receipt_by_stamp_task(
        self,
        request: VerifyReceiptByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyReceiptByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='event',
            function='verifyReceiptByStampTask',
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
                result_type=VerifyReceiptByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_receipt_by_stamp_task(
        self,
        request: VerifyReceiptByStampTaskRequest,
    ) -> VerifyReceiptByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_receipt_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_receipt_by_stamp_task_async(
        self,
        request: VerifyReceiptByStampTaskRequest,
    ) -> VerifyReceiptByStampTaskResult:
        async_result = []
        self._verify_receipt_by_stamp_task(
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

    def _describe_subscription_statuses(
        self,
        request: DescribeSubscriptionStatusesRequest,
        callback: Callable[[AsyncResult[DescribeSubscriptionStatusesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='describeSubscriptionStatuses',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeSubscriptionStatusesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscription_statuses(
        self,
        request: DescribeSubscriptionStatusesRequest,
    ) -> DescribeSubscriptionStatusesResult:
        async_result = []
        with timeout(30):
            self._describe_subscription_statuses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscription_statuses_async(
        self,
        request: DescribeSubscriptionStatusesRequest,
    ) -> DescribeSubscriptionStatusesResult:
        async_result = []
        self._describe_subscription_statuses(
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

    def _describe_subscription_statuses_by_user_id(
        self,
        request: DescribeSubscriptionStatusesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscriptionStatusesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='describeSubscriptionStatusesByUserId',
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
                result_type=DescribeSubscriptionStatusesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscription_statuses_by_user_id(
        self,
        request: DescribeSubscriptionStatusesByUserIdRequest,
    ) -> DescribeSubscriptionStatusesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscription_statuses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscription_statuses_by_user_id_async(
        self,
        request: DescribeSubscriptionStatusesByUserIdRequest,
    ) -> DescribeSubscriptionStatusesByUserIdResult:
        async_result = []
        self._describe_subscription_statuses_by_user_id(
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

    def _get_subscription_status(
        self,
        request: GetSubscriptionStatusRequest,
        callback: Callable[[AsyncResult[GetSubscriptionStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='getSubscriptionStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscriptionStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscription_status(
        self,
        request: GetSubscriptionStatusRequest,
    ) -> GetSubscriptionStatusResult:
        async_result = []
        with timeout(30):
            self._get_subscription_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscription_status_async(
        self,
        request: GetSubscriptionStatusRequest,
    ) -> GetSubscriptionStatusResult:
        async_result = []
        self._get_subscription_status(
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

    def _get_subscription_status_by_user_id(
        self,
        request: GetSubscriptionStatusByUserIdRequest,
        callback: Callable[[AsyncResult[GetSubscriptionStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='getSubscriptionStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.content_name is not None:
            body["contentName"] = request.content_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscriptionStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscription_status_by_user_id(
        self,
        request: GetSubscriptionStatusByUserIdRequest,
    ) -> GetSubscriptionStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_subscription_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscription_status_by_user_id_async(
        self,
        request: GetSubscriptionStatusByUserIdRequest,
    ) -> GetSubscriptionStatusByUserIdResult:
        async_result = []
        self._get_subscription_status_by_user_id(
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

    def _allocate_subscription_status(
        self,
        request: AllocateSubscriptionStatusRequest,
        callback: Callable[[AsyncResult[AllocateSubscriptionStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='allocateSubscriptionStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.receipt is not None:
            body["receipt"] = request.receipt

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AllocateSubscriptionStatusResult,
                callback=callback,
                body=body,
            )
        )

    def allocate_subscription_status(
        self,
        request: AllocateSubscriptionStatusRequest,
    ) -> AllocateSubscriptionStatusResult:
        async_result = []
        with timeout(30):
            self._allocate_subscription_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def allocate_subscription_status_async(
        self,
        request: AllocateSubscriptionStatusRequest,
    ) -> AllocateSubscriptionStatusResult:
        async_result = []
        self._allocate_subscription_status(
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

    def _allocate_subscription_status_by_user_id(
        self,
        request: AllocateSubscriptionStatusByUserIdRequest,
        callback: Callable[[AsyncResult[AllocateSubscriptionStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='allocateSubscriptionStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.receipt is not None:
            body["receipt"] = request.receipt
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AllocateSubscriptionStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def allocate_subscription_status_by_user_id(
        self,
        request: AllocateSubscriptionStatusByUserIdRequest,
    ) -> AllocateSubscriptionStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._allocate_subscription_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def allocate_subscription_status_by_user_id_async(
        self,
        request: AllocateSubscriptionStatusByUserIdRequest,
    ) -> AllocateSubscriptionStatusByUserIdResult:
        async_result = []
        self._allocate_subscription_status_by_user_id(
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

    def _takeover_subscription_status(
        self,
        request: TakeoverSubscriptionStatusRequest,
        callback: Callable[[AsyncResult[TakeoverSubscriptionStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='takeoverSubscriptionStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.receipt is not None:
            body["receipt"] = request.receipt

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=TakeoverSubscriptionStatusResult,
                callback=callback,
                body=body,
            )
        )

    def takeover_subscription_status(
        self,
        request: TakeoverSubscriptionStatusRequest,
    ) -> TakeoverSubscriptionStatusResult:
        async_result = []
        with timeout(30):
            self._takeover_subscription_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def takeover_subscription_status_async(
        self,
        request: TakeoverSubscriptionStatusRequest,
    ) -> TakeoverSubscriptionStatusResult:
        async_result = []
        self._takeover_subscription_status(
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

    def _takeover_subscription_status_by_user_id(
        self,
        request: TakeoverSubscriptionStatusByUserIdRequest,
        callback: Callable[[AsyncResult[TakeoverSubscriptionStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='subscriptionStatus',
            function='takeoverSubscriptionStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.receipt is not None:
            body["receipt"] = request.receipt
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=TakeoverSubscriptionStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def takeover_subscription_status_by_user_id(
        self,
        request: TakeoverSubscriptionStatusByUserIdRequest,
    ) -> TakeoverSubscriptionStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._takeover_subscription_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def takeover_subscription_status_by_user_id_async(
        self,
        request: TakeoverSubscriptionStatusByUserIdRequest,
    ) -> TakeoverSubscriptionStatusByUserIdResult:
        async_result = []
        self._takeover_subscription_status_by_user_id(
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

    def _describe_refund_histories_by_user_id(
        self,
        request: DescribeRefundHistoriesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeRefundHistoriesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='refundHistory',
            function='describeRefundHistoriesByUserId',
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
                result_type=DescribeRefundHistoriesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_refund_histories_by_user_id(
        self,
        request: DescribeRefundHistoriesByUserIdRequest,
    ) -> DescribeRefundHistoriesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_refund_histories_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_refund_histories_by_user_id_async(
        self,
        request: DescribeRefundHistoriesByUserIdRequest,
    ) -> DescribeRefundHistoriesByUserIdResult:
        async_result = []
        self._describe_refund_histories_by_user_id(
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

    def _describe_refund_histories_by_date(
        self,
        request: DescribeRefundHistoriesByDateRequest,
        callback: Callable[[AsyncResult[DescribeRefundHistoriesByDateResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='refundHistory',
            function='describeRefundHistoriesByDate',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.day is not None:
            body["day"] = request.day
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeRefundHistoriesByDateResult,
                callback=callback,
                body=body,
            )
        )

    def describe_refund_histories_by_date(
        self,
        request: DescribeRefundHistoriesByDateRequest,
    ) -> DescribeRefundHistoriesByDateResult:
        async_result = []
        with timeout(30):
            self._describe_refund_histories_by_date(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_refund_histories_by_date_async(
        self,
        request: DescribeRefundHistoriesByDateRequest,
    ) -> DescribeRefundHistoriesByDateResult:
        async_result = []
        self._describe_refund_histories_by_date(
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

    def _get_refund_history(
        self,
        request: GetRefundHistoryRequest,
        callback: Callable[[AsyncResult[GetRefundHistoryResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='refundHistory',
            function='getRefundHistory',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRefundHistoryResult,
                callback=callback,
                body=body,
            )
        )

    def get_refund_history(
        self,
        request: GetRefundHistoryRequest,
    ) -> GetRefundHistoryResult:
        async_result = []
        with timeout(30):
            self._get_refund_history(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_refund_history_async(
        self,
        request: GetRefundHistoryRequest,
    ) -> GetRefundHistoryResult:
        async_result = []
        self._get_refund_history(
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

    def _describe_store_content_models(
        self,
        request: DescribeStoreContentModelsRequest,
        callback: Callable[[AsyncResult[DescribeStoreContentModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModel',
            function='describeStoreContentModels',
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
                result_type=DescribeStoreContentModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_store_content_models(
        self,
        request: DescribeStoreContentModelsRequest,
    ) -> DescribeStoreContentModelsResult:
        async_result = []
        with timeout(30):
            self._describe_store_content_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_store_content_models_async(
        self,
        request: DescribeStoreContentModelsRequest,
    ) -> DescribeStoreContentModelsResult:
        async_result = []
        self._describe_store_content_models(
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

    def _get_store_content_model(
        self,
        request: GetStoreContentModelRequest,
        callback: Callable[[AsyncResult[GetStoreContentModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModel',
            function='getStoreContentModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStoreContentModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_store_content_model(
        self,
        request: GetStoreContentModelRequest,
    ) -> GetStoreContentModelResult:
        async_result = []
        with timeout(30):
            self._get_store_content_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_store_content_model_async(
        self,
        request: GetStoreContentModelRequest,
    ) -> GetStoreContentModelResult:
        async_result = []
        self._get_store_content_model(
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

    def _describe_store_content_model_masters(
        self,
        request: DescribeStoreContentModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeStoreContentModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModelMaster',
            function='describeStoreContentModelMasters',
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
                result_type=DescribeStoreContentModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_store_content_model_masters(
        self,
        request: DescribeStoreContentModelMastersRequest,
    ) -> DescribeStoreContentModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_store_content_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_store_content_model_masters_async(
        self,
        request: DescribeStoreContentModelMastersRequest,
    ) -> DescribeStoreContentModelMastersResult:
        async_result = []
        self._describe_store_content_model_masters(
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

    def _create_store_content_model_master(
        self,
        request: CreateStoreContentModelMasterRequest,
        callback: Callable[[AsyncResult[CreateStoreContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModelMaster',
            function='createStoreContentModelMaster',
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
        if request.apple_app_store is not None:
            body["appleAppStore"] = request.apple_app_store.to_dict()
        if request.google_play is not None:
            body["googlePlay"] = request.google_play.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateStoreContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_store_content_model_master(
        self,
        request: CreateStoreContentModelMasterRequest,
    ) -> CreateStoreContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_store_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_store_content_model_master_async(
        self,
        request: CreateStoreContentModelMasterRequest,
    ) -> CreateStoreContentModelMasterResult:
        async_result = []
        self._create_store_content_model_master(
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

    def _get_store_content_model_master(
        self,
        request: GetStoreContentModelMasterRequest,
        callback: Callable[[AsyncResult[GetStoreContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModelMaster',
            function='getStoreContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStoreContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_store_content_model_master(
        self,
        request: GetStoreContentModelMasterRequest,
    ) -> GetStoreContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_store_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_store_content_model_master_async(
        self,
        request: GetStoreContentModelMasterRequest,
    ) -> GetStoreContentModelMasterResult:
        async_result = []
        self._get_store_content_model_master(
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

    def _update_store_content_model_master(
        self,
        request: UpdateStoreContentModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateStoreContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModelMaster',
            function='updateStoreContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.apple_app_store is not None:
            body["appleAppStore"] = request.apple_app_store.to_dict()
        if request.google_play is not None:
            body["googlePlay"] = request.google_play.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateStoreContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_store_content_model_master(
        self,
        request: UpdateStoreContentModelMasterRequest,
    ) -> UpdateStoreContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_store_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_store_content_model_master_async(
        self,
        request: UpdateStoreContentModelMasterRequest,
    ) -> UpdateStoreContentModelMasterResult:
        async_result = []
        self._update_store_content_model_master(
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

    def _delete_store_content_model_master(
        self,
        request: DeleteStoreContentModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteStoreContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeContentModelMaster',
            function='deleteStoreContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteStoreContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_store_content_model_master(
        self,
        request: DeleteStoreContentModelMasterRequest,
    ) -> DeleteStoreContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_store_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_store_content_model_master_async(
        self,
        request: DeleteStoreContentModelMasterRequest,
    ) -> DeleteStoreContentModelMasterResult:
        async_result = []
        self._delete_store_content_model_master(
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

    def _describe_store_subscription_content_models(
        self,
        request: DescribeStoreSubscriptionContentModelsRequest,
        callback: Callable[[AsyncResult[DescribeStoreSubscriptionContentModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModel',
            function='describeStoreSubscriptionContentModels',
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
                result_type=DescribeStoreSubscriptionContentModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_store_subscription_content_models(
        self,
        request: DescribeStoreSubscriptionContentModelsRequest,
    ) -> DescribeStoreSubscriptionContentModelsResult:
        async_result = []
        with timeout(30):
            self._describe_store_subscription_content_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_store_subscription_content_models_async(
        self,
        request: DescribeStoreSubscriptionContentModelsRequest,
    ) -> DescribeStoreSubscriptionContentModelsResult:
        async_result = []
        self._describe_store_subscription_content_models(
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

    def _get_store_subscription_content_model(
        self,
        request: GetStoreSubscriptionContentModelRequest,
        callback: Callable[[AsyncResult[GetStoreSubscriptionContentModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModel',
            function='getStoreSubscriptionContentModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStoreSubscriptionContentModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_store_subscription_content_model(
        self,
        request: GetStoreSubscriptionContentModelRequest,
    ) -> GetStoreSubscriptionContentModelResult:
        async_result = []
        with timeout(30):
            self._get_store_subscription_content_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_store_subscription_content_model_async(
        self,
        request: GetStoreSubscriptionContentModelRequest,
    ) -> GetStoreSubscriptionContentModelResult:
        async_result = []
        self._get_store_subscription_content_model(
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

    def _describe_store_subscription_content_model_masters(
        self,
        request: DescribeStoreSubscriptionContentModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeStoreSubscriptionContentModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModelMaster',
            function='describeStoreSubscriptionContentModelMasters',
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
                result_type=DescribeStoreSubscriptionContentModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_store_subscription_content_model_masters(
        self,
        request: DescribeStoreSubscriptionContentModelMastersRequest,
    ) -> DescribeStoreSubscriptionContentModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_store_subscription_content_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_store_subscription_content_model_masters_async(
        self,
        request: DescribeStoreSubscriptionContentModelMastersRequest,
    ) -> DescribeStoreSubscriptionContentModelMastersResult:
        async_result = []
        self._describe_store_subscription_content_model_masters(
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

    def _create_store_subscription_content_model_master(
        self,
        request: CreateStoreSubscriptionContentModelMasterRequest,
        callback: Callable[[AsyncResult[CreateStoreSubscriptionContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModelMaster',
            function='createStoreSubscriptionContentModelMaster',
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
        if request.schedule_namespace_id is not None:
            body["scheduleNamespaceId"] = request.schedule_namespace_id
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name
        if request.trigger_extend_mode is not None:
            body["triggerExtendMode"] = request.trigger_extend_mode
        if request.rollup_hour is not None:
            body["rollupHour"] = request.rollup_hour
        if request.reallocate_span_days is not None:
            body["reallocateSpanDays"] = request.reallocate_span_days
        if request.apple_app_store is not None:
            body["appleAppStore"] = request.apple_app_store.to_dict()
        if request.google_play is not None:
            body["googlePlay"] = request.google_play.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateStoreSubscriptionContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_store_subscription_content_model_master(
        self,
        request: CreateStoreSubscriptionContentModelMasterRequest,
    ) -> CreateStoreSubscriptionContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_store_subscription_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_store_subscription_content_model_master_async(
        self,
        request: CreateStoreSubscriptionContentModelMasterRequest,
    ) -> CreateStoreSubscriptionContentModelMasterResult:
        async_result = []
        self._create_store_subscription_content_model_master(
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

    def _get_store_subscription_content_model_master(
        self,
        request: GetStoreSubscriptionContentModelMasterRequest,
        callback: Callable[[AsyncResult[GetStoreSubscriptionContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModelMaster',
            function='getStoreSubscriptionContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStoreSubscriptionContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_store_subscription_content_model_master(
        self,
        request: GetStoreSubscriptionContentModelMasterRequest,
    ) -> GetStoreSubscriptionContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_store_subscription_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_store_subscription_content_model_master_async(
        self,
        request: GetStoreSubscriptionContentModelMasterRequest,
    ) -> GetStoreSubscriptionContentModelMasterResult:
        async_result = []
        self._get_store_subscription_content_model_master(
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

    def _update_store_subscription_content_model_master(
        self,
        request: UpdateStoreSubscriptionContentModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateStoreSubscriptionContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModelMaster',
            function='updateStoreSubscriptionContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.schedule_namespace_id is not None:
            body["scheduleNamespaceId"] = request.schedule_namespace_id
        if request.trigger_name is not None:
            body["triggerName"] = request.trigger_name
        if request.trigger_extend_mode is not None:
            body["triggerExtendMode"] = request.trigger_extend_mode
        if request.rollup_hour is not None:
            body["rollupHour"] = request.rollup_hour
        if request.reallocate_span_days is not None:
            body["reallocateSpanDays"] = request.reallocate_span_days
        if request.apple_app_store is not None:
            body["appleAppStore"] = request.apple_app_store.to_dict()
        if request.google_play is not None:
            body["googlePlay"] = request.google_play.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateStoreSubscriptionContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_store_subscription_content_model_master(
        self,
        request: UpdateStoreSubscriptionContentModelMasterRequest,
    ) -> UpdateStoreSubscriptionContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_store_subscription_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_store_subscription_content_model_master_async(
        self,
        request: UpdateStoreSubscriptionContentModelMasterRequest,
    ) -> UpdateStoreSubscriptionContentModelMasterResult:
        async_result = []
        self._update_store_subscription_content_model_master(
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

    def _delete_store_subscription_content_model_master(
        self,
        request: DeleteStoreSubscriptionContentModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteStoreSubscriptionContentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='storeSubscriptionContentModelMaster',
            function='deleteStoreSubscriptionContentModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.content_name is not None:
            body["contentName"] = request.content_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteStoreSubscriptionContentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_store_subscription_content_model_master(
        self,
        request: DeleteStoreSubscriptionContentModelMasterRequest,
    ) -> DeleteStoreSubscriptionContentModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_store_subscription_content_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_store_subscription_content_model_master_async(
        self,
        request: DeleteStoreSubscriptionContentModelMasterRequest,
    ) -> DeleteStoreSubscriptionContentModelMasterResult:
        async_result = []
        self._delete_store_subscription_content_model_master(
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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
            service="money2",
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

    def _describe_daily_transaction_histories_by_currency(
        self,
        request: DescribeDailyTransactionHistoriesByCurrencyRequest,
        callback: Callable[[AsyncResult[DescribeDailyTransactionHistoriesByCurrencyResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='dailyTransactionHistory',
            function='describeDailyTransactionHistoriesByCurrency',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.currency is not None:
            body["currency"] = request.currency
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeDailyTransactionHistoriesByCurrencyResult,
                callback=callback,
                body=body,
            )
        )

    def describe_daily_transaction_histories_by_currency(
        self,
        request: DescribeDailyTransactionHistoriesByCurrencyRequest,
    ) -> DescribeDailyTransactionHistoriesByCurrencyResult:
        async_result = []
        with timeout(30):
            self._describe_daily_transaction_histories_by_currency(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_daily_transaction_histories_by_currency_async(
        self,
        request: DescribeDailyTransactionHistoriesByCurrencyRequest,
    ) -> DescribeDailyTransactionHistoriesByCurrencyResult:
        async_result = []
        self._describe_daily_transaction_histories_by_currency(
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

    def _describe_daily_transaction_histories(
        self,
        request: DescribeDailyTransactionHistoriesRequest,
        callback: Callable[[AsyncResult[DescribeDailyTransactionHistoriesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='dailyTransactionHistory',
            function='describeDailyTransactionHistories',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.day is not None:
            body["day"] = request.day
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeDailyTransactionHistoriesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_daily_transaction_histories(
        self,
        request: DescribeDailyTransactionHistoriesRequest,
    ) -> DescribeDailyTransactionHistoriesResult:
        async_result = []
        with timeout(30):
            self._describe_daily_transaction_histories(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_daily_transaction_histories_async(
        self,
        request: DescribeDailyTransactionHistoriesRequest,
    ) -> DescribeDailyTransactionHistoriesResult:
        async_result = []
        self._describe_daily_transaction_histories(
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

    def _get_daily_transaction_history(
        self,
        request: GetDailyTransactionHistoryRequest,
        callback: Callable[[AsyncResult[GetDailyTransactionHistoryResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='dailyTransactionHistory',
            function='getDailyTransactionHistory',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.day is not None:
            body["day"] = request.day
        if request.currency is not None:
            body["currency"] = request.currency

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetDailyTransactionHistoryResult,
                callback=callback,
                body=body,
            )
        )

    def get_daily_transaction_history(
        self,
        request: GetDailyTransactionHistoryRequest,
    ) -> GetDailyTransactionHistoryResult:
        async_result = []
        with timeout(30):
            self._get_daily_transaction_history(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_daily_transaction_history_async(
        self,
        request: GetDailyTransactionHistoryRequest,
    ) -> GetDailyTransactionHistoryResult:
        async_result = []
        self._get_daily_transaction_history(
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

    def _describe_unused_balances(
        self,
        request: DescribeUnusedBalancesRequest,
        callback: Callable[[AsyncResult[DescribeUnusedBalancesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='unusedBalance',
            function='describeUnusedBalances',
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
                result_type=DescribeUnusedBalancesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_unused_balances(
        self,
        request: DescribeUnusedBalancesRequest,
    ) -> DescribeUnusedBalancesResult:
        async_result = []
        with timeout(30):
            self._describe_unused_balances(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_unused_balances_async(
        self,
        request: DescribeUnusedBalancesRequest,
    ) -> DescribeUnusedBalancesResult:
        async_result = []
        self._describe_unused_balances(
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

    def _get_unused_balance(
        self,
        request: GetUnusedBalanceRequest,
        callback: Callable[[AsyncResult[GetUnusedBalanceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="money2",
            component='unusedBalance',
            function='getUnusedBalance',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.currency is not None:
            body["currency"] = request.currency

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetUnusedBalanceResult,
                callback=callback,
                body=body,
            )
        )

    def get_unused_balance(
        self,
        request: GetUnusedBalanceRequest,
    ) -> GetUnusedBalanceResult:
        async_result = []
        with timeout(30):
            self._get_unused_balance(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_unused_balance_async(
        self,
        request: GetUnusedBalanceRequest,
    ) -> GetUnusedBalanceResult:
        async_result = []
        self._get_unused_balance(
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