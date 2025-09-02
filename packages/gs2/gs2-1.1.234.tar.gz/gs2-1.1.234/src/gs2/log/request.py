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

from __future__ import annotations

from .model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    type: str = None
    gcp_credential_json: str = None
    big_query_dataset_name: str = None
    log_expire_days: int = None
    aws_region: str = None
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    firehose_stream_name: str = None
    firehose_compress_data: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_type(self, type: str) -> CreateNamespaceRequest:
        self.type = type
        return self

    def with_gcp_credential_json(self, gcp_credential_json: str) -> CreateNamespaceRequest:
        self.gcp_credential_json = gcp_credential_json
        return self

    def with_big_query_dataset_name(self, big_query_dataset_name: str) -> CreateNamespaceRequest:
        self.big_query_dataset_name = big_query_dataset_name
        return self

    def with_log_expire_days(self, log_expire_days: int) -> CreateNamespaceRequest:
        self.log_expire_days = log_expire_days
        return self

    def with_aws_region(self, aws_region: str) -> CreateNamespaceRequest:
        self.aws_region = aws_region
        return self

    def with_aws_access_key_id(self, aws_access_key_id: str) -> CreateNamespaceRequest:
        self.aws_access_key_id = aws_access_key_id
        return self

    def with_aws_secret_access_key(self, aws_secret_access_key: str) -> CreateNamespaceRequest:
        self.aws_secret_access_key = aws_secret_access_key
        return self

    def with_firehose_stream_name(self, firehose_stream_name: str) -> CreateNamespaceRequest:
        self.firehose_stream_name = firehose_stream_name
        return self

    def with_firehose_compress_data(self, firehose_compress_data: str) -> CreateNamespaceRequest:
        self.firehose_compress_data = firehose_compress_data
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_type(data.get('type'))\
            .with_gcp_credential_json(data.get('gcpCredentialJson'))\
            .with_big_query_dataset_name(data.get('bigQueryDatasetName'))\
            .with_log_expire_days(data.get('logExpireDays'))\
            .with_aws_region(data.get('awsRegion'))\
            .with_aws_access_key_id(data.get('awsAccessKeyId'))\
            .with_aws_secret_access_key(data.get('awsSecretAccessKey'))\
            .with_firehose_stream_name(data.get('firehoseStreamName'))\
            .with_firehose_compress_data(data.get('firehoseCompressData'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "gcpCredentialJson": self.gcp_credential_json,
            "bigQueryDatasetName": self.big_query_dataset_name,
            "logExpireDays": self.log_expire_days,
            "awsRegion": self.aws_region,
            "awsAccessKeyId": self.aws_access_key_id,
            "awsSecretAccessKey": self.aws_secret_access_key,
            "firehoseStreamName": self.firehose_stream_name,
            "firehoseCompressData": self.firehose_compress_data,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    type: str = None
    gcp_credential_json: str = None
    big_query_dataset_name: str = None
    log_expire_days: int = None
    aws_region: str = None
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    firehose_stream_name: str = None
    firehose_compress_data: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_type(self, type: str) -> UpdateNamespaceRequest:
        self.type = type
        return self

    def with_gcp_credential_json(self, gcp_credential_json: str) -> UpdateNamespaceRequest:
        self.gcp_credential_json = gcp_credential_json
        return self

    def with_big_query_dataset_name(self, big_query_dataset_name: str) -> UpdateNamespaceRequest:
        self.big_query_dataset_name = big_query_dataset_name
        return self

    def with_log_expire_days(self, log_expire_days: int) -> UpdateNamespaceRequest:
        self.log_expire_days = log_expire_days
        return self

    def with_aws_region(self, aws_region: str) -> UpdateNamespaceRequest:
        self.aws_region = aws_region
        return self

    def with_aws_access_key_id(self, aws_access_key_id: str) -> UpdateNamespaceRequest:
        self.aws_access_key_id = aws_access_key_id
        return self

    def with_aws_secret_access_key(self, aws_secret_access_key: str) -> UpdateNamespaceRequest:
        self.aws_secret_access_key = aws_secret_access_key
        return self

    def with_firehose_stream_name(self, firehose_stream_name: str) -> UpdateNamespaceRequest:
        self.firehose_stream_name = firehose_stream_name
        return self

    def with_firehose_compress_data(self, firehose_compress_data: str) -> UpdateNamespaceRequest:
        self.firehose_compress_data = firehose_compress_data
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_type(data.get('type'))\
            .with_gcp_credential_json(data.get('gcpCredentialJson'))\
            .with_big_query_dataset_name(data.get('bigQueryDatasetName'))\
            .with_log_expire_days(data.get('logExpireDays'))\
            .with_aws_region(data.get('awsRegion'))\
            .with_aws_access_key_id(data.get('awsAccessKeyId'))\
            .with_aws_secret_access_key(data.get('awsSecretAccessKey'))\
            .with_firehose_stream_name(data.get('firehoseStreamName'))\
            .with_firehose_compress_data(data.get('firehoseCompressData'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "type": self.type,
            "gcpCredentialJson": self.gcp_credential_json,
            "bigQueryDatasetName": self.big_query_dataset_name,
            "logExpireDays": self.log_expire_days,
            "awsRegion": self.aws_region,
            "awsAccessKeyId": self.aws_access_key_id,
            "awsSecretAccessKey": self.aws_secret_access_key,
            "firehoseStreamName": self.firehose_stream_name,
            "firehoseCompressData": self.firehose_compress_data,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetServiceVersionRequest(core.Gs2Request):

    context_stack: str = None

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetServiceVersionRequest]:
        if data is None:
            return None
        return GetServiceVersionRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class QueryAccessLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: str = None
    method: str = None
    user_id: str = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryAccessLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: str) -> QueryAccessLogRequest:
        self.service = service
        return self

    def with_method(self, method: str) -> QueryAccessLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> QueryAccessLogRequest:
        self.user_id = user_id
        return self

    def with_begin(self, begin: int) -> QueryAccessLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryAccessLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryAccessLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryAccessLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryAccessLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryAccessLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryAccessLogRequest]:
        if data is None:
            return None
        return QueryAccessLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CountAccessLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: bool = None
    method: bool = None
    user_id: bool = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CountAccessLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: bool) -> CountAccessLogRequest:
        self.service = service
        return self

    def with_method(self, method: bool) -> CountAccessLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: bool) -> CountAccessLogRequest:
        self.user_id = user_id
        return self

    def with_begin(self, begin: int) -> CountAccessLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> CountAccessLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> CountAccessLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> CountAccessLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> CountAccessLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CountAccessLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountAccessLogRequest]:
        if data is None:
            return None
        return CountAccessLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class QueryIssueStampSheetLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryIssueStampSheetLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: str) -> QueryIssueStampSheetLogRequest:
        self.service = service
        return self

    def with_method(self, method: str) -> QueryIssueStampSheetLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> QueryIssueStampSheetLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> QueryIssueStampSheetLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> QueryIssueStampSheetLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryIssueStampSheetLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryIssueStampSheetLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryIssueStampSheetLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryIssueStampSheetLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryIssueStampSheetLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryIssueStampSheetLogRequest]:
        if data is None:
            return None
        return QueryIssueStampSheetLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CountIssueStampSheetLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: bool = None
    method: bool = None
    user_id: bool = None
    action: bool = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CountIssueStampSheetLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: bool) -> CountIssueStampSheetLogRequest:
        self.service = service
        return self

    def with_method(self, method: bool) -> CountIssueStampSheetLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: bool) -> CountIssueStampSheetLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: bool) -> CountIssueStampSheetLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> CountIssueStampSheetLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> CountIssueStampSheetLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> CountIssueStampSheetLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> CountIssueStampSheetLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> CountIssueStampSheetLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CountIssueStampSheetLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountIssueStampSheetLogRequest]:
        if data is None:
            return None
        return CountIssueStampSheetLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class QueryExecuteStampSheetLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryExecuteStampSheetLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: str) -> QueryExecuteStampSheetLogRequest:
        self.service = service
        return self

    def with_method(self, method: str) -> QueryExecuteStampSheetLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> QueryExecuteStampSheetLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> QueryExecuteStampSheetLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> QueryExecuteStampSheetLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryExecuteStampSheetLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryExecuteStampSheetLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryExecuteStampSheetLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryExecuteStampSheetLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryExecuteStampSheetLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryExecuteStampSheetLogRequest]:
        if data is None:
            return None
        return QueryExecuteStampSheetLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CountExecuteStampSheetLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: bool = None
    method: bool = None
    user_id: bool = None
    action: bool = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CountExecuteStampSheetLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: bool) -> CountExecuteStampSheetLogRequest:
        self.service = service
        return self

    def with_method(self, method: bool) -> CountExecuteStampSheetLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: bool) -> CountExecuteStampSheetLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: bool) -> CountExecuteStampSheetLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> CountExecuteStampSheetLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> CountExecuteStampSheetLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> CountExecuteStampSheetLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> CountExecuteStampSheetLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> CountExecuteStampSheetLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CountExecuteStampSheetLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountExecuteStampSheetLogRequest]:
        if data is None:
            return None
        return CountExecuteStampSheetLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class QueryExecuteStampTaskLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: str = None
    method: str = None
    user_id: str = None
    action: str = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryExecuteStampTaskLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: str) -> QueryExecuteStampTaskLogRequest:
        self.service = service
        return self

    def with_method(self, method: str) -> QueryExecuteStampTaskLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: str) -> QueryExecuteStampTaskLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: str) -> QueryExecuteStampTaskLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> QueryExecuteStampTaskLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryExecuteStampTaskLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryExecuteStampTaskLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryExecuteStampTaskLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryExecuteStampTaskLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryExecuteStampTaskLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryExecuteStampTaskLogRequest]:
        if data is None:
            return None
        return QueryExecuteStampTaskLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CountExecuteStampTaskLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    service: bool = None
    method: bool = None
    user_id: bool = None
    action: bool = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> CountExecuteStampTaskLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_service(self, service: bool) -> CountExecuteStampTaskLogRequest:
        self.service = service
        return self

    def with_method(self, method: bool) -> CountExecuteStampTaskLogRequest:
        self.method = method
        return self

    def with_user_id(self, user_id: bool) -> CountExecuteStampTaskLogRequest:
        self.user_id = user_id
        return self

    def with_action(self, action: bool) -> CountExecuteStampTaskLogRequest:
        self.action = action
        return self

    def with_begin(self, begin: int) -> CountExecuteStampTaskLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> CountExecuteStampTaskLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> CountExecuteStampTaskLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> CountExecuteStampTaskLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> CountExecuteStampTaskLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CountExecuteStampTaskLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountExecuteStampTaskLogRequest]:
        if data is None:
            return None
        return CountExecuteStampTaskLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_service(data.get('service'))\
            .with_method(data.get('method'))\
            .with_user_id(data.get('userId'))\
            .with_action(data.get('action'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "service": self.service,
            "method": self.method,
            "userId": self.user_id,
            "action": self.action,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class QueryInGameLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    tags: List[InGameLogTag] = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryInGameLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> QueryInGameLogRequest:
        self.user_id = user_id
        return self

    def with_tags(self, tags: List[InGameLogTag]) -> QueryInGameLogRequest:
        self.tags = tags
        return self

    def with_begin(self, begin: int) -> QueryInGameLogRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryInGameLogRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryInGameLogRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryInGameLogRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryInGameLogRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryInGameLogRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> QueryInGameLogRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryInGameLogRequest]:
        if data is None:
            return None
        return QueryInGameLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_tags(None if data.get('tags') is None else [
                InGameLogTag.from_dict(data.get('tags')[i])
                for i in range(len(data.get('tags')))
            ])\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "tags": None if self.tags is None else [
                self.tags[i].to_dict() if self.tags[i] else None
                for i in range(len(self.tags))
            ],
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class SendInGameLogRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    tags: List[InGameLogTag] = None
    payload: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendInGameLogRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SendInGameLogRequest:
        self.access_token = access_token
        return self

    def with_tags(self, tags: List[InGameLogTag]) -> SendInGameLogRequest:
        self.tags = tags
        return self

    def with_payload(self, payload: str) -> SendInGameLogRequest:
        self.payload = payload
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendInGameLogRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendInGameLogRequest]:
        if data is None:
            return None
        return SendInGameLogRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_tags(None if data.get('tags') is None else [
                InGameLogTag.from_dict(data.get('tags')[i])
                for i in range(len(data.get('tags')))
            ])\
            .with_payload(data.get('payload'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "tags": None if self.tags is None else [
                self.tags[i].to_dict() if self.tags[i] else None
                for i in range(len(self.tags))
            ],
            "payload": self.payload,
        }


class SendInGameLogByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    tags: List[InGameLogTag] = None
    payload: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendInGameLogByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SendInGameLogByUserIdRequest:
        self.user_id = user_id
        return self

    def with_tags(self, tags: List[InGameLogTag]) -> SendInGameLogByUserIdRequest:
        self.tags = tags
        return self

    def with_payload(self, payload: str) -> SendInGameLogByUserIdRequest:
        self.payload = payload
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SendInGameLogByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendInGameLogByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendInGameLogByUserIdRequest]:
        if data is None:
            return None
        return SendInGameLogByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_tags(None if data.get('tags') is None else [
                InGameLogTag.from_dict(data.get('tags')[i])
                for i in range(len(data.get('tags')))
            ])\
            .with_payload(data.get('payload'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "tags": None if self.tags is None else [
                self.tags[i].to_dict() if self.tags[i] else None
                for i in range(len(self.tags))
            ],
            "payload": self.payload,
            "timeOffsetToken": self.time_offset_token,
        }


class QueryAccessLogWithTelemetryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    begin: int = None
    end: int = None
    long_term: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> QueryAccessLogWithTelemetryRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> QueryAccessLogWithTelemetryRequest:
        self.user_id = user_id
        return self

    def with_begin(self, begin: int) -> QueryAccessLogWithTelemetryRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> QueryAccessLogWithTelemetryRequest:
        self.end = end
        return self

    def with_long_term(self, long_term: bool) -> QueryAccessLogWithTelemetryRequest:
        self.long_term = long_term
        return self

    def with_page_token(self, page_token: str) -> QueryAccessLogWithTelemetryRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> QueryAccessLogWithTelemetryRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> QueryAccessLogWithTelemetryRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryAccessLogWithTelemetryRequest]:
        if data is None:
            return None
        return QueryAccessLogWithTelemetryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_long_term(data.get('longTerm'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "begin": self.begin,
            "end": self.end,
            "longTerm": self.long_term,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeInsightsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInsightsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeInsightsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInsightsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeInsightsRequest]:
        if data is None:
            return None
        return DescribeInsightsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateInsightRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateInsightRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateInsightRequest]:
        if data is None:
            return None
        return CreateInsightRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetInsightRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    insight_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInsightRequest:
        self.namespace_name = namespace_name
        return self

    def with_insight_name(self, insight_name: str) -> GetInsightRequest:
        self.insight_name = insight_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetInsightRequest]:
        if data is None:
            return None
        return GetInsightRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_insight_name(data.get('insightName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "insightName": self.insight_name,
        }


class DeleteInsightRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    insight_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteInsightRequest:
        self.namespace_name = namespace_name
        return self

    def with_insight_name(self, insight_name: str) -> DeleteInsightRequest:
        self.insight_name = insight_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteInsightRequest]:
        if data is None:
            return None
        return DeleteInsightRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_insight_name(data.get('insightName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "insightName": self.insight_name,
        }