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

from typing import Any


class timeout:
    def __init__(
            self,
            seconds: int = 1,
            error_message: str = 'Timeout'
    ):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, _: Any, __: Any):
        from multiprocessing import TimeoutError
        raise TimeoutError(self.error_message)

    def __enter__(self) -> None:
        import signal
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, _type, value, traceback) -> None:
        import signal
        signal.alarm(0)
