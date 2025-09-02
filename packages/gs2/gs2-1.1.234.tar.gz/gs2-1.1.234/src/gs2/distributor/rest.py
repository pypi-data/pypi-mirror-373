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


class Gs2DistributorRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
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
            service='distributor',
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
        if request.assume_user_id is not None:
            body["assumeUserId"] = request.assume_user_id
        if request.auto_run_stamp_sheet_notification is not None:
            body["autoRunStampSheetNotification"] = request.auto_run_stamp_sheet_notification.to_dict()
        if request.auto_run_transaction_notification is not None:
            body["autoRunTransactionNotification"] = request.auto_run_transaction_notification.to_dict()
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
            service='distributor',
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
            service='distributor',
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
            service='distributor',
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
        if request.assume_user_id is not None:
            body["assumeUserId"] = request.assume_user_id
        if request.auto_run_stamp_sheet_notification is not None:
            body["autoRunStampSheetNotification"] = request.auto_run_stamp_sheet_notification.to_dict()
        if request.auto_run_transaction_notification is not None:
            body["autoRunTransactionNotification"] = request.auto_run_transaction_notification.to_dict()
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
            service='distributor',
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
            service='distributor',
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

    def _describe_distributor_model_masters(
        self,
        request: DescribeDistributorModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeDistributorModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/master/distributor".format(
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
            result_type=DescribeDistributorModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_distributor_model_masters(
        self,
        request: DescribeDistributorModelMastersRequest,
    ) -> DescribeDistributorModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_distributor_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_distributor_model_masters_async(
        self,
        request: DescribeDistributorModelMastersRequest,
    ) -> DescribeDistributorModelMastersResult:
        async_result = []
        self._describe_distributor_model_masters(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_distributor_model_master(
        self,
        request: CreateDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[CreateDistributorModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/master/distributor".format(
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
        if request.inbox_namespace_id is not None:
            body["inboxNamespaceId"] = request.inbox_namespace_id
        if request.white_list_target_ids is not None:
            body["whiteListTargetIds"] = [
                item
                for item in request.white_list_target_ids
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateDistributorModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_distributor_model_master(
        self,
        request: CreateDistributorModelMasterRequest,
    ) -> CreateDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_distributor_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_distributor_model_master_async(
        self,
        request: CreateDistributorModelMasterRequest,
    ) -> CreateDistributorModelMasterResult:
        async_result = []
        self._create_distributor_model_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_distributor_model_master(
        self,
        request: GetDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[GetDistributorModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/master/distributor/{distributorName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            distributorName=request.distributor_name if request.distributor_name is not None and request.distributor_name != '' else 'null',
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
            result_type=GetDistributorModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_distributor_model_master(
        self,
        request: GetDistributorModelMasterRequest,
    ) -> GetDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_distributor_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_distributor_model_master_async(
        self,
        request: GetDistributorModelMasterRequest,
    ) -> GetDistributorModelMasterResult:
        async_result = []
        self._get_distributor_model_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_distributor_model_master(
        self,
        request: UpdateDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateDistributorModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/master/distributor/{distributorName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            distributorName=request.distributor_name if request.distributor_name is not None and request.distributor_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.inbox_namespace_id is not None:
            body["inboxNamespaceId"] = request.inbox_namespace_id
        if request.white_list_target_ids is not None:
            body["whiteListTargetIds"] = [
                item
                for item in request.white_list_target_ids
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateDistributorModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_distributor_model_master(
        self,
        request: UpdateDistributorModelMasterRequest,
    ) -> UpdateDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_distributor_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_distributor_model_master_async(
        self,
        request: UpdateDistributorModelMasterRequest,
    ) -> UpdateDistributorModelMasterResult:
        async_result = []
        self._update_distributor_model_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_distributor_model_master(
        self,
        request: DeleteDistributorModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteDistributorModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/master/distributor/{distributorName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            distributorName=request.distributor_name if request.distributor_name is not None and request.distributor_name != '' else 'null',
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
            result_type=DeleteDistributorModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_distributor_model_master(
        self,
        request: DeleteDistributorModelMasterRequest,
    ) -> DeleteDistributorModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_distributor_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_distributor_model_master_async(
        self,
        request: DeleteDistributorModelMasterRequest,
    ) -> DeleteDistributorModelMasterResult:
        async_result = []
        self._delete_distributor_model_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_distributor_models(
        self,
        request: DescribeDistributorModelsRequest,
        callback: Callable[[AsyncResult[DescribeDistributorModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distributor".format(
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
            result_type=DescribeDistributorModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_distributor_models(
        self,
        request: DescribeDistributorModelsRequest,
    ) -> DescribeDistributorModelsResult:
        async_result = []
        with timeout(30):
            self._describe_distributor_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_distributor_models_async(
        self,
        request: DescribeDistributorModelsRequest,
    ) -> DescribeDistributorModelsResult:
        async_result = []
        self._describe_distributor_models(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_distributor_model(
        self,
        request: GetDistributorModelRequest,
        callback: Callable[[AsyncResult[GetDistributorModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distributor/{distributorName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            distributorName=request.distributor_name if request.distributor_name is not None and request.distributor_name != '' else 'null',
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
            result_type=GetDistributorModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_distributor_model(
        self,
        request: GetDistributorModelRequest,
    ) -> GetDistributorModelResult:
        async_result = []
        with timeout(30):
            self._get_distributor_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_distributor_model_async(
        self,
        request: GetDistributorModelRequest,
    ) -> GetDistributorModelResult:
        async_result = []
        self._get_distributor_model(
            request,
            lambda result: async_result.append(result),
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
            service='distributor',
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

    def _get_current_distributor_master(
        self,
        request: GetCurrentDistributorMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentDistributorMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
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
            result_type=GetCurrentDistributorMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_current_distributor_master(
        self,
        request: GetCurrentDistributorMasterRequest,
    ) -> GetCurrentDistributorMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_distributor_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_distributor_master_async(
        self,
        request: GetCurrentDistributorMasterRequest,
    ) -> GetCurrentDistributorMasterResult:
        async_result = []
        self._get_current_distributor_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_distributor_master(
        self,
        request: PreUpdateCurrentDistributorMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentDistributorMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
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
            result_type=PreUpdateCurrentDistributorMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def pre_update_current_distributor_master(
        self,
        request: PreUpdateCurrentDistributorMasterRequest,
    ) -> PreUpdateCurrentDistributorMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_distributor_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_distributor_master_async(
        self,
        request: PreUpdateCurrentDistributorMasterRequest,
    ) -> PreUpdateCurrentDistributorMasterResult:
        async_result = []
        self._pre_update_current_distributor_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_distributor_master(
        self,
        request: UpdateCurrentDistributorMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentDistributorMasterResult]], None],
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_distributor_master(
                PreUpdateCurrentDistributorMasterRequest() \
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
            service='distributor',
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
            result_type=UpdateCurrentDistributorMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_distributor_master(
        self,
        request: UpdateCurrentDistributorMasterRequest,
    ) -> UpdateCurrentDistributorMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_distributor_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_distributor_master_async(
        self,
        request: UpdateCurrentDistributorMasterRequest,
    ) -> UpdateCurrentDistributorMasterResult:
        async_result = []
        self._update_current_distributor_master(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_distributor_master_from_git_hub(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentDistributorMasterFromGitHubResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
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
            result_type=UpdateCurrentDistributorMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_distributor_master_from_git_hub(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
    ) -> UpdateCurrentDistributorMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_distributor_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_distributor_master_from_git_hub_async(
        self,
        request: UpdateCurrentDistributorMasterFromGitHubRequest,
    ) -> UpdateCurrentDistributorMasterFromGitHubResult:
        async_result = []
        self._update_current_distributor_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _distribute(
        self,
        request: DistributeRequest,
        callback: Callable[[AsyncResult[DistributeResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distribute/{distributorName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            distributorName=request.distributor_name if request.distributor_name is not None and request.distributor_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.distribute_resource is not None:
            body["distributeResource"] = request.distribute_resource.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DistributeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def distribute(
        self,
        request: DistributeRequest,
    ) -> DistributeResult:
        async_result = []
        with timeout(30):
            self._distribute(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def distribute_async(
        self,
        request: DistributeRequest,
    ) -> DistributeResult:
        async_result = []
        self._distribute(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _distribute_without_overflow_process(
        self,
        request: DistributeWithoutOverflowProcessRequest,
        callback: Callable[[AsyncResult[DistributeWithoutOverflowProcessResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/distribute"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.distribute_resource is not None:
            body["distributeResource"] = request.distribute_resource.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DistributeWithoutOverflowProcessResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def distribute_without_overflow_process(
        self,
        request: DistributeWithoutOverflowProcessRequest,
    ) -> DistributeWithoutOverflowProcessResult:
        async_result = []
        with timeout(30):
            self._distribute_without_overflow_process(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def distribute_without_overflow_process_async(
        self,
        request: DistributeWithoutOverflowProcessRequest,
    ) -> DistributeWithoutOverflowProcessResult:
        async_result = []
        self._distribute_without_overflow_process(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_verify_task(
        self,
        request: RunVerifyTaskRequest,
        callback: Callable[[AsyncResult[RunVerifyTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distribute/stamp/verifyTask/run".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.verify_task is not None:
            body["verifyTask"] = request.verify_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=RunVerifyTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_verify_task(
        self,
        request: RunVerifyTaskRequest,
    ) -> RunVerifyTaskResult:
        async_result = []
        with timeout(30):
            self._run_verify_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_verify_task_async(
        self,
        request: RunVerifyTaskRequest,
    ) -> RunVerifyTaskResult:
        async_result = []
        self._run_verify_task(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_task(
        self,
        request: RunStampTaskRequest,
        callback: Callable[[AsyncResult[RunStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distribute/stamp/task/run".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

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
            result_type=RunStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_task(
        self,
        request: RunStampTaskRequest,
    ) -> RunStampTaskResult:
        async_result = []
        with timeout(30):
            self._run_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_task_async(
        self,
        request: RunStampTaskRequest,
    ) -> RunStampTaskResult:
        async_result = []
        self._run_stamp_task(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_sheet(
        self,
        request: RunStampSheetRequest,
        callback: Callable[[AsyncResult[RunStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distribute/stamp/sheet/run".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

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
            result_type=RunStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_sheet(
        self,
        request: RunStampSheetRequest,
    ) -> RunStampSheetResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_async(
        self,
        request: RunStampSheetRequest,
    ) -> RunStampSheetResult:
        async_result = []
        self._run_stamp_sheet(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_sheet_express(
        self,
        request: RunStampSheetExpressRequest,
        callback: Callable[[AsyncResult[RunStampSheetExpressResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/distribute/stamp/run".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

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
            result_type=RunStampSheetExpressResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_sheet_express(
        self,
        request: RunStampSheetExpressRequest,
    ) -> RunStampSheetExpressResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_express(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_express_async(
        self,
        request: RunStampSheetExpressRequest,
    ) -> RunStampSheetExpressResult:
        async_result = []
        self._run_stamp_sheet_express(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_verify_task_without_namespace(
        self,
        request: RunVerifyTaskWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunVerifyTaskWithoutNamespaceResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/verifyTask/run"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.verify_task is not None:
            body["verifyTask"] = request.verify_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=RunVerifyTaskWithoutNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_verify_task_without_namespace(
        self,
        request: RunVerifyTaskWithoutNamespaceRequest,
    ) -> RunVerifyTaskWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_verify_task_without_namespace(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_verify_task_without_namespace_async(
        self,
        request: RunVerifyTaskWithoutNamespaceRequest,
    ) -> RunVerifyTaskWithoutNamespaceResult:
        async_result = []
        self._run_verify_task_without_namespace(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_task_without_namespace(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampTaskWithoutNamespaceResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/task/run"

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
            result_type=RunStampTaskWithoutNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_task_without_namespace(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
    ) -> RunStampTaskWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_task_without_namespace(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_task_without_namespace_async(
        self,
        request: RunStampTaskWithoutNamespaceRequest,
    ) -> RunStampTaskWithoutNamespaceResult:
        async_result = []
        self._run_stamp_task_without_namespace(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_sheet_without_namespace(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampSheetWithoutNamespaceResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/sheet/run"

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
            result_type=RunStampSheetWithoutNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_sheet_without_namespace(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
    ) -> RunStampSheetWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_without_namespace(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_without_namespace_async(
        self,
        request: RunStampSheetWithoutNamespaceRequest,
    ) -> RunStampSheetWithoutNamespaceResult:
        async_result = []
        self._run_stamp_sheet_without_namespace(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_stamp_sheet_express_without_namespace(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
        callback: Callable[[AsyncResult[RunStampSheetExpressWithoutNamespaceResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/run"

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
            result_type=RunStampSheetExpressWithoutNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_stamp_sheet_express_without_namespace(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
    ) -> RunStampSheetExpressWithoutNamespaceResult:
        async_result = []
        with timeout(30):
            self._run_stamp_sheet_express_without_namespace(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_stamp_sheet_express_without_namespace_async(
        self,
        request: RunStampSheetExpressWithoutNamespaceRequest,
    ) -> RunStampSheetExpressWithoutNamespaceResult:
        async_result = []
        self._run_stamp_sheet_express_without_namespace(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_transaction_default_config(
        self,
        request: SetTransactionDefaultConfigRequest,
        callback: Callable[[AsyncResult[SetTransactionDefaultConfigResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/transaction/user/me/config"

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
            result_type=SetTransactionDefaultConfigResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_transaction_default_config(
        self,
        request: SetTransactionDefaultConfigRequest,
    ) -> SetTransactionDefaultConfigResult:
        async_result = []
        with timeout(30):
            self._set_transaction_default_config(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_transaction_default_config_async(
        self,
        request: SetTransactionDefaultConfigRequest,
    ) -> SetTransactionDefaultConfigResult:
        async_result = []
        self._set_transaction_default_config(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_transaction_default_config_by_user_id(
        self,
        request: SetTransactionDefaultConfigByUserIdRequest,
        callback: Callable[[AsyncResult[SetTransactionDefaultConfigByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/transaction/user/{userId}/config".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
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
            result_type=SetTransactionDefaultConfigByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_transaction_default_config_by_user_id(
        self,
        request: SetTransactionDefaultConfigByUserIdRequest,
    ) -> SetTransactionDefaultConfigByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_transaction_default_config_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_transaction_default_config_by_user_id_async(
        self,
        request: SetTransactionDefaultConfigByUserIdRequest,
    ) -> SetTransactionDefaultConfigByUserIdResult:
        async_result = []
        self._set_transaction_default_config_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _freeze_master_data(
        self,
        request: FreezeMasterDataRequest,
        callback: Callable[[AsyncResult[FreezeMasterDataResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/masterdata/freeze".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=FreezeMasterDataResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def freeze_master_data(
        self,
        request: FreezeMasterDataRequest,
    ) -> FreezeMasterDataResult:
        async_result = []
        with timeout(30):
            self._freeze_master_data(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def freeze_master_data_async(
        self,
        request: FreezeMasterDataRequest,
    ) -> FreezeMasterDataResult:
        async_result = []
        self._freeze_master_data(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _freeze_master_data_by_user_id(
        self,
        request: FreezeMasterDataByUserIdRequest,
        callback: Callable[[AsyncResult[FreezeMasterDataByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/masterdata/freeze".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
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
            result_type=FreezeMasterDataByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def freeze_master_data_by_user_id(
        self,
        request: FreezeMasterDataByUserIdRequest,
    ) -> FreezeMasterDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._freeze_master_data_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def freeze_master_data_by_user_id_async(
        self,
        request: FreezeMasterDataByUserIdRequest,
    ) -> FreezeMasterDataByUserIdResult:
        async_result = []
        self._freeze_master_data_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sign_freeze_master_data_timestamp(
        self,
        request: SignFreezeMasterDataTimestampRequest,
        callback: Callable[[AsyncResult[SignFreezeMasterDataTimestampResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/masterdata/freeze/timestamp".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.timestamp is not None:
            body["timestamp"] = request.timestamp
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SignFreezeMasterDataTimestampResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def sign_freeze_master_data_timestamp(
        self,
        request: SignFreezeMasterDataTimestampRequest,
    ) -> SignFreezeMasterDataTimestampResult:
        async_result = []
        with timeout(30):
            self._sign_freeze_master_data_timestamp(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sign_freeze_master_data_timestamp_async(
        self,
        request: SignFreezeMasterDataTimestampRequest,
    ) -> SignFreezeMasterDataTimestampResult:
        async_result = []
        self._sign_freeze_master_data_timestamp(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _freeze_master_data_by_signed_timestamp(
        self,
        request: FreezeMasterDataBySignedTimestampRequest,
        callback: Callable[[AsyncResult[FreezeMasterDataBySignedTimestampResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/masterdata/freeze/timestamp".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.body is not None:
            body["body"] = request.body
        if request.signature is not None:
            body["signature"] = request.signature
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=FreezeMasterDataBySignedTimestampResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def freeze_master_data_by_signed_timestamp(
        self,
        request: FreezeMasterDataBySignedTimestampRequest,
    ) -> FreezeMasterDataBySignedTimestampResult:
        async_result = []
        with timeout(30):
            self._freeze_master_data_by_signed_timestamp(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def freeze_master_data_by_signed_timestamp_async(
        self,
        request: FreezeMasterDataBySignedTimestampRequest,
    ) -> FreezeMasterDataBySignedTimestampResult:
        async_result = []
        self._freeze_master_data_by_signed_timestamp(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _freeze_master_data_by_timestamp(
        self,
        request: FreezeMasterDataByTimestampRequest,
        callback: Callable[[AsyncResult[FreezeMasterDataByTimestampResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/masterdata/freeze/timestamp/raw".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.timestamp is not None:
            body["timestamp"] = request.timestamp

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=FreezeMasterDataByTimestampResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def freeze_master_data_by_timestamp(
        self,
        request: FreezeMasterDataByTimestampRequest,
    ) -> FreezeMasterDataByTimestampResult:
        async_result = []
        with timeout(30):
            self._freeze_master_data_by_timestamp(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def freeze_master_data_by_timestamp_async(
        self,
        request: FreezeMasterDataByTimestampRequest,
    ) -> FreezeMasterDataByTimestampResult:
        async_result = []
        self._freeze_master_data_by_timestamp(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _batch_execute_api(
        self,
        request: BatchExecuteApiRequest,
        callback: Callable[[AsyncResult[BatchExecuteApiResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/batch/execute"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.request_payloads is not None:
            body["requestPayloads"] = [
                item.to_dict()
                for item in request.request_payloads
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=BatchExecuteApiResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def batch_execute_api(
        self,
        request: BatchExecuteApiRequest,
    ) -> BatchExecuteApiResult:
        async_result = []
        with timeout(30):
            self._batch_execute_api(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_execute_api_async(
        self,
        request: BatchExecuteApiRequest,
    ) -> BatchExecuteApiResult:
        async_result = []
        self._batch_execute_api(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _if_expression_by_user_id(
        self,
        request: IfExpressionByUserIdRequest,
        callback: Callable[[AsyncResult[IfExpressionByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/expression/if".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.condition is not None:
            body["condition"] = request.condition.to_dict()
        if request.true_actions is not None:
            body["trueActions"] = [
                item.to_dict()
                for item in request.true_actions
            ]
        if request.false_actions is not None:
            body["falseActions"] = [
                item.to_dict()
                for item in request.false_actions
            ]
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
            result_type=IfExpressionByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def if_expression_by_user_id(
        self,
        request: IfExpressionByUserIdRequest,
    ) -> IfExpressionByUserIdResult:
        async_result = []
        with timeout(30):
            self._if_expression_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def if_expression_by_user_id_async(
        self,
        request: IfExpressionByUserIdRequest,
    ) -> IfExpressionByUserIdResult:
        async_result = []
        self._if_expression_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _and_expression_by_user_id(
        self,
        request: AndExpressionByUserIdRequest,
        callback: Callable[[AsyncResult[AndExpressionByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/expression/and".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.actions is not None:
            body["actions"] = [
                item.to_dict()
                for item in request.actions
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
            result_type=AndExpressionByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def and_expression_by_user_id(
        self,
        request: AndExpressionByUserIdRequest,
    ) -> AndExpressionByUserIdResult:
        async_result = []
        with timeout(30):
            self._and_expression_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def and_expression_by_user_id_async(
        self,
        request: AndExpressionByUserIdRequest,
    ) -> AndExpressionByUserIdResult:
        async_result = []
        self._and_expression_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _or_expression_by_user_id(
        self,
        request: OrExpressionByUserIdRequest,
        callback: Callable[[AsyncResult[OrExpressionByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/expression/or".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.actions is not None:
            body["actions"] = [
                item.to_dict()
                for item in request.actions
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
            result_type=OrExpressionByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def or_expression_by_user_id(
        self,
        request: OrExpressionByUserIdRequest,
    ) -> OrExpressionByUserIdResult:
        async_result = []
        with timeout(30):
            self._or_expression_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def or_expression_by_user_id_async(
        self,
        request: OrExpressionByUserIdRequest,
    ) -> OrExpressionByUserIdResult:
        async_result = []
        self._or_expression_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _if_expression_by_stamp_task(
        self,
        request: IfExpressionByStampTaskRequest,
        callback: Callable[[AsyncResult[IfExpressionByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/expression/if"

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
            result_type=IfExpressionByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def if_expression_by_stamp_task(
        self,
        request: IfExpressionByStampTaskRequest,
    ) -> IfExpressionByStampTaskResult:
        async_result = []
        with timeout(30):
            self._if_expression_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def if_expression_by_stamp_task_async(
        self,
        request: IfExpressionByStampTaskRequest,
    ) -> IfExpressionByStampTaskResult:
        async_result = []
        self._if_expression_by_stamp_task(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _and_expression_by_stamp_task(
        self,
        request: AndExpressionByStampTaskRequest,
        callback: Callable[[AsyncResult[AndExpressionByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/expression/and"

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
            result_type=AndExpressionByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def and_expression_by_stamp_task(
        self,
        request: AndExpressionByStampTaskRequest,
    ) -> AndExpressionByStampTaskResult:
        async_result = []
        with timeout(30):
            self._and_expression_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def and_expression_by_stamp_task_async(
        self,
        request: AndExpressionByStampTaskRequest,
    ) -> AndExpressionByStampTaskResult:
        async_result = []
        self._and_expression_by_stamp_task(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _or_expression_by_stamp_task(
        self,
        request: OrExpressionByStampTaskRequest,
        callback: Callable[[AsyncResult[OrExpressionByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/stamp/expression/or"

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
            result_type=OrExpressionByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def or_expression_by_stamp_task(
        self,
        request: OrExpressionByStampTaskRequest,
    ) -> OrExpressionByStampTaskResult:
        async_result = []
        with timeout(30):
            self._or_expression_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def or_expression_by_stamp_task_async(
        self,
        request: OrExpressionByStampTaskRequest,
    ) -> OrExpressionByStampTaskResult:
        async_result = []
        self._or_expression_by_stamp_task(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_stamp_sheet_result(
        self,
        request: GetStampSheetResultRequest,
        callback: Callable[[AsyncResult[GetStampSheetResultResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stampSheet/{transactionId}/result".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            transactionId=request.transaction_id if request.transaction_id is not None and request.transaction_id != '' else 'null',
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
            result_type=GetStampSheetResultResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamp_sheet_result(
        self,
        request: GetStampSheetResultRequest,
    ) -> GetStampSheetResultResult:
        async_result = []
        with timeout(30):
            self._get_stamp_sheet_result(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamp_sheet_result_async(
        self,
        request: GetStampSheetResultRequest,
    ) -> GetStampSheetResultResult:
        async_result = []
        self._get_stamp_sheet_result(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_stamp_sheet_result_by_user_id(
        self,
        request: GetStampSheetResultByUserIdRequest,
        callback: Callable[[AsyncResult[GetStampSheetResultByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stampSheet/{transactionId}/result".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            transactionId=request.transaction_id if request.transaction_id is not None and request.transaction_id != '' else 'null',
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
            result_type=GetStampSheetResultByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamp_sheet_result_by_user_id(
        self,
        request: GetStampSheetResultByUserIdRequest,
    ) -> GetStampSheetResultByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_stamp_sheet_result_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamp_sheet_result_by_user_id_async(
        self,
        request: GetStampSheetResultByUserIdRequest,
    ) -> GetStampSheetResultByUserIdResult:
        async_result = []
        self._get_stamp_sheet_result_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _run_transaction(
        self,
        request: RunTransactionRequest,
        callback: Callable[[AsyncResult[RunTransactionResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/system/{ownerId}/{namespaceName}/user/{userId}/transaction/run".format(
            ownerId=request.owner_id if request.owner_id is not None and request.owner_id != '' else 'null',
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.transaction is not None:
            body["transaction"] = request.transaction

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=RunTransactionResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def run_transaction(
        self,
        request: RunTransactionRequest,
    ) -> RunTransactionResult:
        async_result = []
        with timeout(30):
            self._run_transaction(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def run_transaction_async(
        self,
        request: RunTransactionRequest,
    ) -> RunTransactionResult:
        async_result = []
        self._run_transaction(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_transaction_result(
        self,
        request: GetTransactionResultRequest,
        callback: Callable[[AsyncResult[GetTransactionResultResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/transaction/{transactionId}/result".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            transactionId=request.transaction_id if request.transaction_id is not None and request.transaction_id != '' else 'null',
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
            result_type=GetTransactionResultResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_transaction_result(
        self,
        request: GetTransactionResultRequest,
    ) -> GetTransactionResultResult:
        async_result = []
        with timeout(30):
            self._get_transaction_result(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_transaction_result_async(
        self,
        request: GetTransactionResultRequest,
    ) -> GetTransactionResultResult:
        async_result = []
        self._get_transaction_result(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_transaction_result_by_user_id(
        self,
        request: GetTransactionResultByUserIdRequest,
        callback: Callable[[AsyncResult[GetTransactionResultByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='distributor',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/transaction/{transactionId}/result".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            transactionId=request.transaction_id if request.transaction_id is not None and request.transaction_id != '' else 'null',
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
            result_type=GetTransactionResultByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_transaction_result_by_user_id(
        self,
        request: GetTransactionResultByUserIdRequest,
    ) -> GetTransactionResultByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_transaction_result_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_transaction_result_by_user_id_async(
        self,
        request: GetTransactionResultByUserIdRequest,
    ) -> GetTransactionResultByUserIdResult:
        async_result = []
        self._get_transaction_result_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result