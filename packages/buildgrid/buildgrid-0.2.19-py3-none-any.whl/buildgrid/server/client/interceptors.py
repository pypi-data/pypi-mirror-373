# Copyright (C) 2019 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Any, Protocol

import grpc
from grpc import aio


class InterceptorFunc(Protocol):
    def amend_call_details(  # type: ignore[no-untyped-def]
        self, client_call_details, grpc_call_details_class: Any
    ) -> Any: ...


class SyncUnaryUnaryInterceptor(grpc.UnaryUnaryClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        new_details = self.func.amend_call_details(client_call_details, grpc.ClientCallDetails)
        return continuation(new_details, request)


class SyncUnaryStreamInterceptor(grpc.UnaryStreamClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        new_details = self.func.amend_call_details(client_call_details, grpc.ClientCallDetails)
        return continuation(new_details, request)


class SyncStreamUnaryInterceptor(grpc.StreamUnaryClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    def intercept_stream_unary(  # type: ignore[no-untyped-def]
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self.func.amend_call_details(client_call_details, grpc.ClientCallDetails)
        return continuation(new_details, request_iterator)


class SyncStreamStreamInterceptor(grpc.StreamStreamClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    def intercept_stream_stream(  # type: ignore[no-untyped-def]
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self.func.amend_call_details(client_call_details, grpc.ClientCallDetails)
        return continuation(new_details, request_iterator)


class AsyncUnaryUnaryInterceptor(aio.UnaryUnaryClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        new_details = self.func.amend_call_details(client_call_details, aio.ClientCallDetails)
        return await continuation(new_details, request)


class AsyncUnaryStreamInterceptor(aio.UnaryStreamClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore[no-untyped-def]
        new_details = self.func.amend_call_details(client_call_details, aio.ClientCallDetails)
        return await continuation(new_details, request)


class AsyncStreamUnaryInterceptor(aio.StreamUnaryClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    async def intercept_stream_unary(  # type: ignore[no-untyped-def]
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self.func.amend_call_details(client_call_details, aio.ClientCallDetails)
        return await continuation(new_details, request_iterator)


class AsyncStreamStreamInterceptor(aio.StreamStreamClientInterceptor):  # type: ignore[type-arg]
    def __init__(self, func: InterceptorFunc):
        self.func = func

    async def intercept_stream_stream(  # type: ignore[no-untyped-def]
        self, continuation, client_call_details, request_iterator
    ):
        new_details = self.func.amend_call_details(client_call_details, aio.ClientCallDetails)
        return await continuation(new_details, request_iterator)
