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


class Gs2MegaFieldWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
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
            service="megaField",
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
            service="megaField",
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
            service="megaField",
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
            service="megaField",
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
            service="megaField",
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
            service="megaField",
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

    def _describe_area_models(
        self,
        request: DescribeAreaModelsRequest,
        callback: Callable[[AsyncResult[DescribeAreaModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModel',
            function='describeAreaModels',
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
                result_type=DescribeAreaModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_area_models(
        self,
        request: DescribeAreaModelsRequest,
    ) -> DescribeAreaModelsResult:
        async_result = []
        with timeout(30):
            self._describe_area_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_area_models_async(
        self,
        request: DescribeAreaModelsRequest,
    ) -> DescribeAreaModelsResult:
        async_result = []
        self._describe_area_models(
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

    def _get_area_model(
        self,
        request: GetAreaModelRequest,
        callback: Callable[[AsyncResult[GetAreaModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModel',
            function='getAreaModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetAreaModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_area_model(
        self,
        request: GetAreaModelRequest,
    ) -> GetAreaModelResult:
        async_result = []
        with timeout(30):
            self._get_area_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_area_model_async(
        self,
        request: GetAreaModelRequest,
    ) -> GetAreaModelResult:
        async_result = []
        self._get_area_model(
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

    def _describe_area_model_masters(
        self,
        request: DescribeAreaModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeAreaModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModelMaster',
            function='describeAreaModelMasters',
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
                result_type=DescribeAreaModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_area_model_masters(
        self,
        request: DescribeAreaModelMastersRequest,
    ) -> DescribeAreaModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_area_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_area_model_masters_async(
        self,
        request: DescribeAreaModelMastersRequest,
    ) -> DescribeAreaModelMastersResult:
        async_result = []
        self._describe_area_model_masters(
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

    def _create_area_model_master(
        self,
        request: CreateAreaModelMasterRequest,
        callback: Callable[[AsyncResult[CreateAreaModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModelMaster',
            function='createAreaModelMaster',
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

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateAreaModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_area_model_master(
        self,
        request: CreateAreaModelMasterRequest,
    ) -> CreateAreaModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_area_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_area_model_master_async(
        self,
        request: CreateAreaModelMasterRequest,
    ) -> CreateAreaModelMasterResult:
        async_result = []
        self._create_area_model_master(
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

    def _get_area_model_master(
        self,
        request: GetAreaModelMasterRequest,
        callback: Callable[[AsyncResult[GetAreaModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModelMaster',
            function='getAreaModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetAreaModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_area_model_master(
        self,
        request: GetAreaModelMasterRequest,
    ) -> GetAreaModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_area_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_area_model_master_async(
        self,
        request: GetAreaModelMasterRequest,
    ) -> GetAreaModelMasterResult:
        async_result = []
        self._get_area_model_master(
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

    def _update_area_model_master(
        self,
        request: UpdateAreaModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateAreaModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModelMaster',
            function='updateAreaModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateAreaModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_area_model_master(
        self,
        request: UpdateAreaModelMasterRequest,
    ) -> UpdateAreaModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_area_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_area_model_master_async(
        self,
        request: UpdateAreaModelMasterRequest,
    ) -> UpdateAreaModelMasterResult:
        async_result = []
        self._update_area_model_master(
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

    def _delete_area_model_master(
        self,
        request: DeleteAreaModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteAreaModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='areaModelMaster',
            function='deleteAreaModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteAreaModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_area_model_master(
        self,
        request: DeleteAreaModelMasterRequest,
    ) -> DeleteAreaModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_area_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_area_model_master_async(
        self,
        request: DeleteAreaModelMasterRequest,
    ) -> DeleteAreaModelMasterResult:
        async_result = []
        self._delete_area_model_master(
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

    def _describe_layer_models(
        self,
        request: DescribeLayerModelsRequest,
        callback: Callable[[AsyncResult[DescribeLayerModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModel',
            function='describeLayerModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeLayerModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_layer_models(
        self,
        request: DescribeLayerModelsRequest,
    ) -> DescribeLayerModelsResult:
        async_result = []
        with timeout(30):
            self._describe_layer_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_layer_models_async(
        self,
        request: DescribeLayerModelsRequest,
    ) -> DescribeLayerModelsResult:
        async_result = []
        self._describe_layer_models(
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

    def _get_layer_model(
        self,
        request: GetLayerModelRequest,
        callback: Callable[[AsyncResult[GetLayerModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModel',
            function='getLayerModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLayerModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_layer_model(
        self,
        request: GetLayerModelRequest,
    ) -> GetLayerModelResult:
        async_result = []
        with timeout(30):
            self._get_layer_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_layer_model_async(
        self,
        request: GetLayerModelRequest,
    ) -> GetLayerModelResult:
        async_result = []
        self._get_layer_model(
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

    def _describe_layer_model_masters(
        self,
        request: DescribeLayerModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeLayerModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModelMaster',
            function='describeLayerModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeLayerModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_layer_model_masters(
        self,
        request: DescribeLayerModelMastersRequest,
    ) -> DescribeLayerModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_layer_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_layer_model_masters_async(
        self,
        request: DescribeLayerModelMastersRequest,
    ) -> DescribeLayerModelMastersResult:
        async_result = []
        self._describe_layer_model_masters(
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

    def _create_layer_model_master(
        self,
        request: CreateLayerModelMasterRequest,
        callback: Callable[[AsyncResult[CreateLayerModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModelMaster',
            function='createLayerModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateLayerModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_layer_model_master(
        self,
        request: CreateLayerModelMasterRequest,
    ) -> CreateLayerModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_layer_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_layer_model_master_async(
        self,
        request: CreateLayerModelMasterRequest,
    ) -> CreateLayerModelMasterResult:
        async_result = []
        self._create_layer_model_master(
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

    def _get_layer_model_master(
        self,
        request: GetLayerModelMasterRequest,
        callback: Callable[[AsyncResult[GetLayerModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModelMaster',
            function='getLayerModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLayerModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_layer_model_master(
        self,
        request: GetLayerModelMasterRequest,
    ) -> GetLayerModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_layer_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_layer_model_master_async(
        self,
        request: GetLayerModelMasterRequest,
    ) -> GetLayerModelMasterResult:
        async_result = []
        self._get_layer_model_master(
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

    def _update_layer_model_master(
        self,
        request: UpdateLayerModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateLayerModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModelMaster',
            function='updateLayerModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateLayerModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_layer_model_master(
        self,
        request: UpdateLayerModelMasterRequest,
    ) -> UpdateLayerModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_layer_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_layer_model_master_async(
        self,
        request: UpdateLayerModelMasterRequest,
    ) -> UpdateLayerModelMasterResult:
        async_result = []
        self._update_layer_model_master(
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

    def _delete_layer_model_master(
        self,
        request: DeleteLayerModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteLayerModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='layerModelMaster',
            function='deleteLayerModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteLayerModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_layer_model_master(
        self,
        request: DeleteLayerModelMasterRequest,
    ) -> DeleteLayerModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_layer_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_layer_model_master_async(
        self,
        request: DeleteLayerModelMasterRequest,
    ) -> DeleteLayerModelMasterResult:
        async_result = []
        self._delete_layer_model_master(
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
            service="megaField",
            component='currentFieldMaster',
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

    def _get_current_field_master(
        self,
        request: GetCurrentFieldMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentFieldMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='currentFieldMaster',
            function='getCurrentFieldMaster',
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
                result_type=GetCurrentFieldMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_field_master(
        self,
        request: GetCurrentFieldMasterRequest,
    ) -> GetCurrentFieldMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_field_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_field_master_async(
        self,
        request: GetCurrentFieldMasterRequest,
    ) -> GetCurrentFieldMasterResult:
        async_result = []
        self._get_current_field_master(
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

    def _pre_update_current_field_master(
        self,
        request: PreUpdateCurrentFieldMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentFieldMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='currentFieldMaster',
            function='preUpdateCurrentFieldMaster',
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
                result_type=PreUpdateCurrentFieldMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_field_master(
        self,
        request: PreUpdateCurrentFieldMasterRequest,
    ) -> PreUpdateCurrentFieldMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_field_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_field_master_async(
        self,
        request: PreUpdateCurrentFieldMasterRequest,
    ) -> PreUpdateCurrentFieldMasterResult:
        async_result = []
        self._pre_update_current_field_master(
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

    def _update_current_field_master(
        self,
        request: UpdateCurrentFieldMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentFieldMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='currentFieldMaster',
            function='updateCurrentFieldMaster',
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
                result_type=UpdateCurrentFieldMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_field_master(
        self,
        request: UpdateCurrentFieldMasterRequest,
    ) -> UpdateCurrentFieldMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_field_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_field_master_async(
        self,
        request: UpdateCurrentFieldMasterRequest,
    ) -> UpdateCurrentFieldMasterResult:
        async_result = []
        self._update_current_field_master(
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

    def _update_current_field_master_from_git_hub(
        self,
        request: UpdateCurrentFieldMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentFieldMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='currentFieldMaster',
            function='updateCurrentFieldMasterFromGitHub',
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
                result_type=UpdateCurrentFieldMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_field_master_from_git_hub(
        self,
        request: UpdateCurrentFieldMasterFromGitHubRequest,
    ) -> UpdateCurrentFieldMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_field_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_field_master_from_git_hub_async(
        self,
        request: UpdateCurrentFieldMasterFromGitHubRequest,
    ) -> UpdateCurrentFieldMasterFromGitHubResult:
        async_result = []
        self._update_current_field_master_from_git_hub(
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

    def _put_position(
        self,
        request: PutPositionRequest,
        callback: Callable[[AsyncResult[PutPositionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='putPosition',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.position is not None:
            body["position"] = request.position.to_dict()
        if request.vector is not None:
            body["vector"] = request.vector.to_dict()
        if request.r is not None:
            body["r"] = request.r

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutPositionResult,
                callback=callback,
                body=body,
            )
        )

    def put_position(
        self,
        request: PutPositionRequest,
    ) -> PutPositionResult:
        async_result = []
        with timeout(30):
            self._put_position(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_position_async(
        self,
        request: PutPositionRequest,
    ) -> PutPositionResult:
        async_result = []
        self._put_position(
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

    def _put_position_by_user_id(
        self,
        request: PutPositionByUserIdRequest,
        callback: Callable[[AsyncResult[PutPositionByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='putPositionByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.position is not None:
            body["position"] = request.position.to_dict()
        if request.vector is not None:
            body["vector"] = request.vector.to_dict()
        if request.r is not None:
            body["r"] = request.r
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutPositionByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def put_position_by_user_id(
        self,
        request: PutPositionByUserIdRequest,
    ) -> PutPositionByUserIdResult:
        async_result = []
        with timeout(30):
            self._put_position_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_position_by_user_id_async(
        self,
        request: PutPositionByUserIdRequest,
    ) -> PutPositionByUserIdResult:
        async_result = []
        self._put_position_by_user_id(
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

    def _fetch_position(
        self,
        request: FetchPositionRequest,
        callback: Callable[[AsyncResult[FetchPositionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='fetchPosition',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.user_ids is not None:
            body["userIds"] = [
                item
                for item in request.user_ids
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
                result_type=FetchPositionResult,
                callback=callback,
                body=body,
            )
        )

    def fetch_position(
        self,
        request: FetchPositionRequest,
    ) -> FetchPositionResult:
        async_result = []
        with timeout(30):
            self._fetch_position(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def fetch_position_async(
        self,
        request: FetchPositionRequest,
    ) -> FetchPositionResult:
        async_result = []
        self._fetch_position(
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

    def _fetch_position_from_system(
        self,
        request: FetchPositionFromSystemRequest,
        callback: Callable[[AsyncResult[FetchPositionFromSystemResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='fetchPositionFromSystem',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.user_ids is not None:
            body["userIds"] = [
                item
                for item in request.user_ids
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=FetchPositionFromSystemResult,
                callback=callback,
                body=body,
            )
        )

    def fetch_position_from_system(
        self,
        request: FetchPositionFromSystemRequest,
    ) -> FetchPositionFromSystemResult:
        async_result = []
        with timeout(30):
            self._fetch_position_from_system(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def fetch_position_from_system_async(
        self,
        request: FetchPositionFromSystemRequest,
    ) -> FetchPositionFromSystemResult:
        async_result = []
        self._fetch_position_from_system(
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

    def _near_user_ids(
        self,
        request: NearUserIdsRequest,
        callback: Callable[[AsyncResult[NearUserIdsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='nearUserIds',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.point is not None:
            body["point"] = request.point.to_dict()
        if request.r is not None:
            body["r"] = request.r
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=NearUserIdsResult,
                callback=callback,
                body=body,
            )
        )

    def near_user_ids(
        self,
        request: NearUserIdsRequest,
    ) -> NearUserIdsResult:
        async_result = []
        with timeout(30):
            self._near_user_ids(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def near_user_ids_async(
        self,
        request: NearUserIdsRequest,
    ) -> NearUserIdsResult:
        async_result = []
        self._near_user_ids(
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

    def _near_user_ids_from_system(
        self,
        request: NearUserIdsFromSystemRequest,
        callback: Callable[[AsyncResult[NearUserIdsFromSystemResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='nearUserIdsFromSystem',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.point is not None:
            body["point"] = request.point.to_dict()
        if request.r is not None:
            body["r"] = request.r
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=NearUserIdsFromSystemResult,
                callback=callback,
                body=body,
            )
        )

    def near_user_ids_from_system(
        self,
        request: NearUserIdsFromSystemRequest,
    ) -> NearUserIdsFromSystemResult:
        async_result = []
        with timeout(30):
            self._near_user_ids_from_system(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def near_user_ids_from_system_async(
        self,
        request: NearUserIdsFromSystemRequest,
    ) -> NearUserIdsFromSystemResult:
        async_result = []
        self._near_user_ids_from_system(
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

    def _action(
        self,
        request: ActionRequest,
        callback: Callable[[AsyncResult[ActionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='action',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.position is not None:
            body["position"] = request.position.to_dict()
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
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
                result_type=ActionResult,
                callback=callback,
                body=body,
            )
        )

    def action(
        self,
        request: ActionRequest,
    ) -> ActionResult:
        async_result = []
        with timeout(30):
            self._action(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def action_async(
        self,
        request: ActionRequest,
    ) -> ActionResult:
        async_result = []
        self._action(
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

    def _action_by_user_id(
        self,
        request: ActionByUserIdRequest,
        callback: Callable[[AsyncResult[ActionByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="megaField",
            component='spatial',
            function='actionByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.area_model_name is not None:
            body["areaModelName"] = request.area_model_name
        if request.layer_model_name is not None:
            body["layerModelName"] = request.layer_model_name
        if request.position is not None:
            body["position"] = request.position.to_dict()
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
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
                result_type=ActionByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def action_by_user_id(
        self,
        request: ActionByUserIdRequest,
    ) -> ActionByUserIdResult:
        async_result = []
        with timeout(30):
            self._action_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def action_by_user_id_async(
        self,
        request: ActionByUserIdRequest,
    ) -> ActionByUserIdResult:
        async_result = []
        self._action_by_user_id(
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