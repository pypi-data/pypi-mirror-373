#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import json
import logging
from typing import TYPE_CHECKING
from aiohttp.client import ClientSession
from aiohttp.formdata import FormData
from aiohttp.client_exceptions import ClientOSError,                    \
                                      ServerDisconnectedError

from requests.sessions import Session
from requests.models import Request as Request_
from urllib.request import Request
from typing import Any
from tenacity.asyncio import AsyncRetrying
from tenacity.retry import retry_if_not_result,                         \
                           retry_if_result,                             \
                           retry_if_exception_type
from tenacity.stop import stop_after_attempt,                           \
                          stop_after_delay
from tenacity.wait import wait_fixed
from tenacity import RetryError
from tenacity.before import before_log
from tenacity.after import after_log

from galaxy.net.net import Client,                                      \
                           AsyncClient
from galaxy.net.http.request import HTTPRequestBuilder
from galaxy.net.http.response import HTTPResponseFactory
from galaxy.service import constant
from galaxy.utils.base import Component,                                \
                              Configurable
from galaxy.service.service import LogService,                          \
                                   LogAsyncService
from galaxy.error.net import NetHTTPInternalServerError
from galaxy.perfo.decorator import timed,                               \
                                   async_timed

if TYPE_CHECKING:
    from galaxy.net.http.session import HTTPSessionFactory,             \
                                        HTTPAsyncSessionFactory,        \
                                        UrllibHTTPSessionFactory,       \
                                        RequestsHTTPSessionFactory,     \
                                        AioHTTPAsyncSessionFactory


class HTTPClient(Client):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPClient, self).__init__()
        self.reqreps: dict[str, HTTPRequestReply] | None = None
        self.session_fact: HTTPSessionFactory | None = None

    def _load(self) -> None:
        super(HTTPClient, self)._load()
        [reqrep._load() for reqrep in self.reqreps.values()]

    def _connect(self) -> None:
        super(HTTPClient, self)._connect()

    def _close(self) -> None:
        super(HTTPClient, self)._close()

    def _get_formatted_body(self, request: Request) -> str:
        return request.data

    def __repr__(self) -> str:
        return "<HTTPClient(id='{}')>".format(self.id)


class UrllibHTTPClient(HTTPClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(UrllibHTTPClient, self).__init__()
        self.reqreps: dict[str, HTTPRequestReply] | None = None
        self.session_fact: UrllibHTTPSessionFactory | None = None
        self.session: ClientSession | None = None

    @timed
    def _load(self) -> None:
        super(UrllibHTTPClient, self)._load()
        if self.session_fact is not None:
            self.session_fact._load()

    @timed
    def _connect(self) -> None:
        self.session = self.session_fact.create(self)
        if self.session is None:
            raise

    @timed
    def send(self, request: Request, resp_format: str) -> Any:
        self.log.logger.debug("Send the HTTP {} request {} with data {} and headers {}".format(request.method,
                                                                                               request.get_full_url(),
                                                                                               request.data,
                                                                                               request.headers))
        request.headers.update({"Cookie": self.session.cookies})
        resp = self.session.pool_manager.request(request.method.upper(),
                                                 request.get_full_url(),
                                                 body=self._get_formatted_body(request),
                                                 headers=request.headers)
        if resp.status != 200:
            self.close()
            raise NetHTTPInternalServerError(resp.status)
        cookies = resp.headers.get("Set-Cookie")
        if cookies:
            self.session.cookies.update(cookies)
        if resp_format == "json":
            return resp.json()
        else:
            return resp.data

    @timed
    def _close(self) -> None:
        self.session.close()

    def _get_formatted_body(self, request: Request) -> [str, dict[str, str]]:
        if "content_type" in request.headers:
            if request.headers["content_type"] == "application/json":
                return json.dumps(request.data)
            elif request.headers["content_type"] == "application/x-www-form-urlencoded":
                return request.data
        return request.data

    def __repr__(self) -> str:
        return "<UrllibHTTPClient(id='{}')>".format(self.id)


class RequestsHTTPClient(HTTPClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RequestsHTTPClient, self).__init__()
        self.reqreps: dict[str, HTTPRequestReply] | None = None
        self.session_fact: RequestsHTTPSessionFactory | None = None
        self.session: Session | None = None

    @timed
    def _load(self) -> None:
        super(RequestsHTTPClient, self)._load()
        if self.session_fact is not None:
            self.session_fact._load()

    @timed
    def _connect(self) -> None:
        self.session = self.session_fact.create(self)
        if self.session is None:
            raise

    @timed
    def send(self, request: Request, resp_format: str) -> Any:
        data = self._get_formatted_body(request)
        self.log.logger.debug("Send the HTTP {} request {} with data {} and headers {}".format(request.method,
                                                                                               request.get_full_url(),
                                                                                               data,
                                                                                               request.headers))
        req = Request_(request.method.upper(),
                       request.get_full_url(),
                       data=data,
                       headers=request.headers)
        prepped = self.session.prepare_request(req)
        try:
            resp = self.session.send(prepped)
        except Exception as e:
            print(e)
        if resp.status_code != 200:
            self.close()
            raise NetHTTPInternalServerError(resp.status_code)
        if resp_format == "json":
            return resp.json()
        elif resp_format == "txt":
            return resp.text
        else:
            return resp.content

    @timed
    def _close(self) -> None:
        self.session.close()

    def _get_formatted_body(self, request: Request) -> [str, dict[str, str]]:
        headers = {k.lower().replace("-", "_"): v for k, v in request.headers.items()}
        if "content_type" in headers:
            if headers["content_type"] == "application/json":
                return json.dumps(request.data)
            elif headers["content_type"] == "application/x-www-form-urlencoded":
                return request.data
        return request.data

    def __repr__(self) -> str:
        return "<RequestsHTTPClient(id='{}')>".format(self.id)


class HTTPAsyncClient(AsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPAsyncClient, self).__init__()
        self.reqreps: dict[str, HTTPRequestReply] | None = None
        self.session_fact: HTTPAsyncSessionFactory | None = None

    async def _load(self) -> None:
        await super(HTTPAsyncClient, self)._load()
        [reqrep._load() for reqrep in self.reqreps.values()]

    async def _connect(self) -> None:
        await super(HTTPAsyncClient, self)._connect()

    async def _close(self) -> None:
        await super(HTTPAsyncClient, self)._close()

    def _get_formatted_body(self, request: Request) -> [str, FormData]:
        return request.data

    def __repr__(self) -> str:
        return "<HTTPAsyncClient(id='{}')>".format(self.id)


class AioHTTPAsyncClient(HTTPAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioHTTPAsyncClient, self).__init__()
        self.reqreps: dict[str, HTTPRequestReply] | None = None
        self.session_fact: AioHTTPAsyncSessionFactory | None = None
        self.session: ClientSession | None = None

    @async_timed
    async def _load(self) -> None:
        await super(AioHTTPAsyncClient, self)._load()
        if self.session_fact is not None:
            self.session_fact._load()

    @async_timed
    async def _connect(self) -> None:
        self.session = await self.session_fact.create(self)
        if self.session is None:
            raise

    @async_timed
    async def _send(self, request: Request, resp_format: str, attempt_nb: int) -> tuple[int, Any]:
        res = None
        data = self._get_formatted_body(request)
        self.log.logger.debug("Send the HTTP {} request {} (Attempt {}) with data {} and headers {}".format(request.method,
                                                                                                            request.get_full_url(),
                                                                                                            attempt_nb,
                                                                                                            data,
                                                                                                            request.headers))
        try:
            async with self.session.request(request.method.lower(),
                                            request.get_full_url(),
                                            data=data,
                                            headers=request.headers) as resp:
                status = resp.status
                self.log.logger.debug("The HTTP {} request {} (Attempt {}) returns with status {}".format(request.method,
                                                                                                          request.get_full_url(),
                                                                                                          attempt_nb,
                                                                                                          status))
                if status == 200:
                    if resp_format == "json":
                        res = await resp.json()
                    elif resp_format == "txt":
                        res = await resp.text()
        except Exception as e:
            self.log.logger.error("The HTTP {} request {} (Attempt {}) fails with the exception '{}'".format(request.method,
                                                                                                             request.get_full_url(),
                                                                                                             attempt_nb,
                                                                                                             str(e)))
            raise e
        return (status, res)

    # Sending HTTP request with asyncio timeout-
    @async_timed
    async def _send_with_timeout(self, request: Request, resp_format: str, attempt_nb: int) -> tuple[int, Any]:
        if "timeout" in self.session_fact.conf:
            timeout = self.session_fact.conf["timeout"].get("total", 120)
            try:
                self.log.logger.debug("Send the HTTP {} request {} (Attempt {}) with a timeout of {} sec".format(request.method,
                                                                                                                 request.get_full_url(),
                                                                                                                 attempt_nb,
                                                                                                                 timeout))
                status, resp = await asyncio.wait_for(self._send(request, resp_format, attempt_nb), timeout)
                # in Python 3.11 :
                #async with asyncio.timeout(timeout):
                #    status, resp = await self._send_request(request, resp_format, attempt_nb)
            except asyncio.TimeoutError as e:
                self.log.logger.error("The HTTP {} request {} (Attempt {}) fails with a timeout of {} sec".format(request.method,
                                                                                                                  request.get_full_url(),
                                                                                                                  attempt_nb,
                                                                                                                  timeout))
                raise e
        else:
            status, resp = await self._send(request, resp_format, attempt_nb)
        return (status, resp)

    @async_timed
    async def send(self, request: Request, resp_format: str) -> Any:
        resp = None
        kwargs = {
                  "retry": (retry_if_not_result(lambda s: s == 200) |
                            retry_if_exception_type(ConnectionResetError) |
                            retry_if_exception_type(asyncio.TimeoutError) |
                            retry_if_exception_type(asyncio.CancelledError) |
                            retry_if_exception_type(ClientOSError) |
                            retry_if_exception_type(ServerDisconnectedError)),
                  "before": before_log(self.log.logger, logging.DEBUG),
                  "after": after_log(self.log.logger, logging.DEBUG)
                 }
        if self.is_connected:
            if "retries" in self.session_fact.conf:
                retries = self.session_fact.conf["retries"].get("total", 1)
                kwargs["stop"] = stop_after_attempt(retries)
            #stop_after_delay does not seem to work :
            #if "timeout" in self.session_fact.conf:
            #    timeout = self.session_fact.conf["timeout"].get("total", 120)
            #    kwargs["stop"] |= stop_after_delay(timeout)
        if "req_interval" in self.session_fact.conf:
            kwargs["wait"] = wait_fixed(self.session_fact.conf["req_interval"])
        try:
            async for attempt in AsyncRetrying(**kwargs):
                with attempt:
                    status, resp = await self._send(request, resp_format, attempt.retry_state.attempt_number)
                if not attempt.retry_state.outcome.failed:
                    attempt.retry_state.set_result(status)
                    if status != 200:
                        self.log.logger.error("The HTTP {} request {} (Attempt {}) fails with status {}".format(request.method,
                                                                                                                request.get_full_url(),
                                                                                                                attempt.retry_state.attempt_number,
                                                                                                                status))
        except RetryError:
            pass
        return resp

    # @async_timed
    # async def send(self, request: Request, resp_format: str) -> Any:
    #     kwargs = {
    #               "retry": retry_if_result(lambda resp: resp is None),
    #               "before": before_log(self.log.logger, logging.DEBUG),
    #               "after": after_log(self.log.logger, logging.DEBUG)
    #              }
    #     if "reconnect_interval" in self.conf:
    #         kwargs["wait"] = wait_fixed(self.conf["reconnect_interval"])
    #     reconnecting = False
    #     try:
    #         async for attempt in AsyncRetrying(**kwargs):
    #             with attempt:
    #                 if reconnecting:
    #                     await self.connect()
    #                     reconnecting = False
    #                 resp = await self._send_with_retries(request, resp_format)
    #                 if resp is None and self.state != constant.STATE_CLOSED:
    #                     if "reconnect_interval" in self.conf:
    #                         self.log.logger.error("The HTTP {} request {} fails : starting to reconnect after {} sec".format(request.method,
    #                                                                                                                          request.get_full_url(),
    #                                                                                                                          self.conf["reconnect_interval"]))
    #                     else:
    #                         self.log.logger.error("The HTTP {} request {} fails : starting to reconnect".format(request.method,
    #                                                                                                             request.get_full_url()))
    #                     await self.close()
    #                     reconnecting = True
    #             if not attempt.retry_state.outcome.failed:
    #                 attempt.retry_state.set_result(resp)
    #     except RetryError:
    #         pass
    #     return resp

    @async_timed
    async def _close(self) -> None:
        await self.session.close()

    def _get_formatted_body(self, request: Request) -> [str, FormData]:
        headers = {k.lower().replace("-", "_"):v for k,v in request.headers.items()}
        if "content_type" in headers:
            if headers["content_type"] == "application/json":
                return json.dumps(request.data)
            elif headers["content_type"] == "application/x-www-form-urlencoded":
                return FormData(request.data, charset="utf-8")
        return request.data

    def __repr__(self) -> str:
        return "<AioHTTPAsyncClient(id='{}')>".format(self.id)


class HTTPRequestReply(Component, Configurable):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | LogAsyncService | None = None
        self.req_builder: HTTPRequestBuilder | None = None
        self.resp_fact: HTTPResponseFactory | None = None

    def __repr__(self) -> str:
        return "<HTTPRequestReply(id='{}')>".format(self.id)
