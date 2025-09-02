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
from typing import List

from ..core.model import RequestError


class Gs2Exception(IOError):

    def __init__(self, message):
        super(Gs2Exception, self).__init__(message)

        self.__errors = []

        errors = None

        try:
            import json
            _ = json.loads(message)
            if isinstance(_, dict):
                errors = json.loads(_['message'])
        except ValueError:
            pass

        if isinstance(errors, list):
            for error in errors:
                if isinstance(error, dict):
                    try:
                        self.__errors.append(
                            RequestError(
                                component=str(error.get('component')),
                                message=str(error.get('message')),
                                code=str(error.get('code')),
                            )
                        )
                    except ValueError:
                        pass

    @property
    def errors(self) -> List[RequestError]:
        """
        エラー一覧を取得する
        :return: エラー一覧
        """
        return self.__errors

    def get_errors(self) -> List[RequestError]:
        """
        エラー一覧を取得する
        :return: エラー一覧
        """
        return self.__errors

    def __getitem__(self, key):
        if key == 'errors':
            return self.get_errors()
        return super(object, self).__getitem__(key)

    def get(self, key, default=None):
        if key == 'errors':
            return self.get_errors()
        try:
            return super(object, self).__getitem__(key)
        except ValueError:
            return default


class BadGatewayException(Gs2Exception):

    def __init__(self, message):
        super(BadGatewayException, self).__init__(message)


class BadRequestException(Gs2Exception):

    def __init__(self, message):
        super(BadRequestException, self).__init__(message)


class ConflictException(Gs2Exception):

    def __init__(self, message):
        super(ConflictException, self).__init__(message)


class InternalServerErrorException(Gs2Exception):

    def __init__(self, message):
        super(InternalServerErrorException, self).__init__(message)


class NotFoundException(Gs2Exception):

    def __init__(self, message):
        super(NotFoundException, self).__init__(message)


class QuotaExceedException(Gs2Exception):

    def __init__(self, message):
        super(QuotaExceedException, self).__init__(message)


class RequestTimeoutException(Gs2Exception):

    def __init__(self, message):
        super(RequestTimeoutException, self).__init__(message)


class ServiceUnavailableException(Gs2Exception):

    def __init__(self, message):
        super(ServiceUnavailableException, self).__init__(message)


class UnauthorizedException(Gs2Exception):

    def __init__(self, message):
        super(UnauthorizedException, self).__init__(message)


class UnknownException(Gs2Exception):

    def __init__(self, message):
        super(UnknownException, self).__init__(message)
