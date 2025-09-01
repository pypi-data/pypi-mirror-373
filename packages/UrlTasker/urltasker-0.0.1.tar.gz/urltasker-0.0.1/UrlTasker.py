#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    A Python library for defining, templating, and executing configurable
#    asynchronous actions triggered via URLs.
#    Copyright (C) 2025  UrlTasker

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
A Python library for defining, templating, and executing configurable
asynchronous actions triggered via URLs.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
A Python library for defining, templating, and executing configurable
asynchronous actions triggered via URLs.
"""
__url__ = "https://github.com/mauricelambert/UrlTasker"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = """
UrlTasker  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from PegParser import (
    HttpResponse,
    HttpRequest,
    StandardRules,
    get_matchs,
    parse_http_response,
)
from ssl import (
    create_default_context,
    _create_unverified_context,
    SSLWantReadError,
    SSLWantWriteError,
    MemoryBIO,
    SSLObject,
)
from asyncio import (
    open_connection,
    create_subprocess_exec,
    gather,
    run,
    sleep,
    get_running_loop,
    AbstractEventLoop,
)
from socket import socket, AF_INET, SOCK_STREAM, gaierror
from typing import Dict, List, Tuple, Coroutine, Union
from urllib.parse import unquote, quote, parse_qsl
from abc import ABC, abstractmethod
from asyncio.subprocess import PIPE
from collections import namedtuple
from dataclasses import dataclass
from sys import exit, executable
from types import FunctionType
from json import loads, dumps
from functools import partial
from base64 import b64encode
from threading import Thread
from os import environ


@dataclass
class ProcessRequest:
    """
    Dataclass to contains elements about the Process to start it.
    """

    executable: str
    arguments: List[str]
    environ: Dict[str, str]
    body: bytes


@dataclass
class ProcessResponse:
    """
    Dataclass to contains elements about the process to returns result.
    """

    code: int
    body: bytes
    error: bytes


WebScriptsResponse = namedtuple(
    "WebScriptsResponse", ["body", "error", "code"]
)


async def handle_python(
    url: Dict[str, List[bytearray]],
    **kwargs,
) -> ProcessResponse:
    """
    Run a subprocess asynchronously using full path and argument list.
    Sends input_data to STDIN (if provided), and captures STDOUT and STDERR.
    """

    if query := url.get("query"):
        query[0] = query[0][1:]
        query[0] = b"?" + url["path"][0] + b"&" + query[0]
    else:
        url["query"][0] = b"?" + url["path"][0]
    url["path"] = (quote(executable).encode(),)
    return await handle_executable(url)


async def handle_executable(
    url: Dict[str, List[bytearray]],
    **kwargs,
) -> ProcessResponse:
    """
    Run a subprocess asynchronously using full path and argument list.
    Sends input_data to STDIN (if provided), and captures STDOUT and STDERR.
    """

    child_environ = environ.copy()

    if parameters := url.get("form_data"):
        for name, value in parse_qsl(parameters[0].decode()):
            child_environ[name.upper()] = unquote(value)

    if url.get("query"):
        url["query"][0] = url["query"][0][1:]  # remove '?'
        arguments = []
        for name, value in parse_qsl(url["query"][0].decode(), True):
            if name:
                arguments.append(unquote(name))
            if value:
                arguments.append(unquote(value))

    return await run_executable(
        ProcessRequest(
            unquote(url["path"][0].decode()),
            arguments,
            child_environ,
            unquote(
                url["fragment"][0][1:].decode("latin-1"), encoding="latin-1"
            ).encode("latin-1"),
        )
    )


async def run_executable(
    request: ProcessRequest,
    **kwargs,
) -> ProcessResponse:
    """
    Run a subprocess asynchronously using full path and argument list.
    Sends input_data to STDIN (if provided), and captures STDOUT and STDERR.
    """

    request.environ.update(kwargs)

    process = await create_subprocess_exec(
        request.executable,
        *request.arguments,
        stdin=PIPE if request.body else None,
        stdout=PIPE,
        stderr=PIPE,
        env=request.environ,
    )

    stdout, stderr = await process.communicate(input=request.body)

    return ProcessResponse(process.returncode, stdout, stderr)


async def handle_webscripts(
    url: Dict[str, List[bytearray]],
    **kwargs,
) -> WebScriptsResponse:
    """
    This function sends an async WebScripts requests from an URL.
    """

    options = b""
    scheme = url["scheme"][0]
    if b"+" in scheme:
        scheme, options = scheme.split(b"+", 1)
        options = b"+" + options

    url["scheme"][0] = b"http" + scheme[10:] + b"+POST" + options
    arguments = {}
    body = {"arguments": arguments}

    if query := url.get("query"):
        query = query[0]
        if len(query) > 1:
            for name, value in parse_qsl(query[1:].decode(), True):
                if name in arguments:
                    argument = arguments[name]
                    if isinstance(argument, list):
                        argument["value"].append(value)
                    else:
                        argument["value"] = [argument["value"], value]
                else:
                    arguments[name] = {"value": value, "input": False}
        del url["query"]

    if fragment := url.get("fragment"):
        arguments["<inputs>"] = {
            "value": unquote(fragment[0][1:].decode()),
            "input": True,
        }

    url["path"] = (b"/api/scripts" + url["path"][0],)
    url["fragment"] = (b"#" + quote(dumps(body)).encode(),)
    headers = url.get("form_data", [])

    old_headers = None
    if headers:
        old_headers = headers.copy()

    headers.append(b"Content-Type=application/json%3B%20charset%3Dutf8")
    url["form_data"] = headers

    response = await handle_method_http_body(url)

    if response.code != 200:
        return WebScriptsResponse(None, None, response.code)

    out = err = ""
    url["scheme"] = (b"http" + scheme[10:] + options,)
    content = loads(response.body.decode())
    if old_headers:
        url["form_data"] = old_headers
    else:
        del url["form_data"]

    while key := content.get("key"):
        url["path"] = (b"/api/script/get/" + key.encode(),)
        out += content["stdout"]
        err += content["stdout"]
        response = await handle_method_http_body(url)

        if response.code != 200:
            content["error"] += "\nHTTP error on /api/script/get/ " + str(
                response.code
            )
            break

        content = loads(response.body.decode())

    return WebScriptsResponse(
        out + content["stdout"],
        err + content["stderr"] + content["error"],
        content["code"],
    )


async def handle_method_http_body(
    url: Dict[str, List[bytearray]],
    **kwargs,
) -> HttpResponse:
    """
    This function is the asynchronous HTTP handle to perform complete request
    and receive response.
    """

    scheme = url["scheme"][0]
    if b"+" in scheme:
        scheme, method, *options = scheme.decode().split("+")
        insecure = "insecure" in options
    else:
        scheme = scheme.decode()
        insecure = False
        method = "GET"

    body = b""
    headers = []

    if fragment := url.get("fragment"):
        body = unquote(fragment[0][1:].decode()).encode()
        del url["fragment"]
    # headers = [
    #     (name, value)
    #     for name, values in parse_qs(url["form_data"]).items()
    #     for value in values
    # ]
    if parameters := url.get("form_data"):
        headers = parse_qsl(parameters[0].decode())
    if url.get("parameters"):
        del url["parameters"]
    url["scheme"] = (scheme.encode(),)

    return await handle_http(
        url, method, body, headers, 1.1, insecure, **kwargs
    )


async def handle_http(
    url: Dict[str, List[bytearray]],
    method: str = "GET",
    body: bytes = b"",
    headers: List[Tuple[str, str]] = [],
    version: float = 1.0,
    insecure: bool = False,
    **kwargs,
) -> HttpResponse:
    """
    This function is the asynchronous HTTP handle to perform request
    and receive response.
    """

    use_ssl = url["scheme"][0][-1] == 115 or url["scheme"][0][-1] == 83

    if host_port := url.get("host_port"):
        port = int(host_port[0].rsplit(b":", 1)[1].decode())
    elif use_ssl:
        port = 443
    else:
        port = 80

    if credentials := url.get("user_info"):
        headers.append(
            ("Authorization", "Basic" + b64encode(credentials[0]).decode())
        )

    origin = False
    host = False
    for header in headers:
        if header[0] == "Origin":
            origin = True
        elif header[0] == "Host":
            host = True

    if not host:
        headers.append(
            ("Host", (url.get("host_port", url["host"])[0]).decode())
        )

    if not origin:
        headers.append(
            (
                "Origin",
                (
                    url["scheme"][0]
                    + b"://"
                    + url.get("host_port", url["host"])[0]
                ).decode(),
            )
        )

    return await http_request(
        HttpRequest(
            method,
            (
                url["path"][0]
                + url.get("parameters", (b"",))[0]
                + url.get("query", (b"",))[0]
            ).decode(),
            b"HTTP",
            version,
            headers,
            body,
            host=url["host"][0].decode(),
        ),
        port,
        use_ssl,
        insecure,
        **kwargs,
    )


# async def http_request(
#     request: HttpRequest, port: int, use_ssl: bool, insecure: bool
# ) -> HttpResponse:
#     """
#     This function performs the async HTTP request,
#     receives and parses the HTTP response.
#     """

#     ssl_context = (_create_unverified_context() if insecure else create_default_context()) if use_ssl else None
#     reader, writer = await open_connection(request.host, port, ssl=ssl_context)

#     writer.write(bytes(request))
#     await writer.drain()

#     data = bytearray()
#     while b"\r\n\r\n" not in data:
#         data.extend(await reader.read(1024))
#         print("HTTP request", data)

#     response = parse_http_response(data)
#     while len(response.body) < response.content_length:
#         print("HTTP request", len(response.body), response.content_length)
#         response.body += await reader.read(
#             response.content_length - len(response.body)
#         )

#     writer.close()
#     await writer.wait_closed()

#     return response


class SocketAsync:

    def __init__(self):
        self.loop = get_running_loop()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setblocking(False)
        self.ssl_manager = None

    async def connect(self, destination: Tuple[str, int]) -> None:
        """
        This method connect the async socket.
        """

        try:
            await self.loop.sock_connect(self.socket, destination)
        except OSError as e:
            if e.errno == 121:
                raise gaierror(
                    "TimeoutError: [WinError 10060] or [Errno 11001] getaddrinfo failed"
                ) from e
            raise e

    async def start_ssl(self, insecure: bool = False) -> None:
        """
        This method starts the TLS connection.
        """

        self.context = (
            _create_unverified_context()
            if insecure
            else create_default_context()
        )
        self.ssl_input = MemoryBIO()
        self.ssl_output = MemoryBIO()
        self.ssl_manager = self.context.wrap_bio(
            self.ssl_input, self.ssl_output, server_side=False
        )

        handshake = False
        await sleep(0)  # await loop.sock_sendall(raw_sock, b'')

        while not handshake:
            try:
                self.ssl_manager.do_handshake()
            except SSLWantReadError:
                await self.sendall()
                data = await self.loop.sock_recv(self.socket, 4096)
                self.ssl_input.write(data)
            except SSLWantWriteError:
                await self.sendall()
            else:
                handshake = True

    async def sendall(self, data: bytes = None) -> None:
        """
        This methods sends data to server with SSL encryption.
        """

        if self.ssl_manager is None:
            await self.loop.sock_sendall(self.socket, data)
            return None

        read = True

        if data is not None:
            self.ssl_manager.write(data)

        while read:
            try:
                encrypted_data = self.ssl_output.read(4096)
            except SSLWantReadError:
                read = False
            else:
                if encrypted_data:
                    await self.loop.sock_sendall(self.socket, encrypted_data)
                else:
                    read = False

    async def recv(self) -> bytearray:
        """
        This method receives encrypted data from server with SSL encryption.
        """

        if self.ssl_manager is None:
            return await self.loop.sock_recv(self.socket, 4096)

        # write = True
        # data = bytearray()

        # while write:
        #     try:
        #         chunk = self.ssl_manager.read(4096)
        #     except SSLWantReadError:
        #         encrypted_data = await self.loop.sock_recv(self.socket, 4096)
        #         self.ssl_input.write(encrypted_data)
        #     else:
        #         write = bool(chunk)
        #         data.extend(chunk)

        # return data

        encrypted_data = await self.loop.sock_recv(self.socket, 4096)
        self.ssl_input.write(encrypted_data)
        return self.ssl_manager.read(4096)


async def http_request(
    request: HttpRequest,
    port: int,
    use_ssl: bool,
    insecure: bool,
    **kwargs,
) -> HttpResponse:
    """
    Perform an async HTTP request and return the parsed HTTP response.
    This version avoids Windows IOCP timeouts by using loop.sock_recv().
    """

    sock = SocketAsync()
    await sock.connect((request.host, port))

    if use_ssl:
        await sock.start_ssl(insecure)

    await sock.sendall(bytes(request))

    buffer = bytearray()
    while b"\r\n\r\n" not in buffer:
        chunk = await sock.recv()
        if not chunk:
            raise ConnectionError(
                "Connection closed before headers were received."
            )
        buffer.extend(chunk)

    header, _, body = buffer.partition(b"\r\n\r\n")
    response = parse_http_response(header + b"\r\n\r\n")
    response.body = bytearray(body)

    while len(response.body) < response.content_length:
        chunk = await sock.recv()
        if not chunk:
            break
        response.body.extend(chunk)

    sock.socket.close()
    return response


class Task(ABC):
    """
    This class implements the abstract class for tasks.
    """

    def __init__(
        self,
        code: Union[FunctionType, Coroutine],
        is_awaitable: bool,
        value: Union[WebScriptsResponse, HttpResponse, ProcessResponse] = None,
    ):
        self.code = code
        self.is_awaitable = is_awaitable
        self.value = value

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError


class SyncTask(Task):
    """
    This class implements a synchronous task.
    """

    def run(self) -> None:
        """
        This method run this synchronous task.
        """

        self.value = self.code()


class AsyncTask(Task):
    """
    This class implements an asynchronous task.
    """

    async def run(self) -> None:
        """
        This method run this asynchronous task.
        """

        self.value = await self.code


class TaskFactory:
    """
    This class implements the task builder.
    """

    @staticmethod
    def create(code: Union[FunctionType, Coroutine]) -> Task:
        """
        This method implements builts the task.
        """

        if isinstance(code, Coroutine):
            return AsyncTask(code, True)
        elif isinstance(code, FunctionType):
            return SyncTask(code, False)
        else:
            raise TypeError("code must be a Coroutine or a Function")


def get_task(url: str, **kwargs: Dict[str, str]) -> Task:
    """
    This function returns a code (function or coroutine) to run url as task.
    """

    position, match = StandardRules.Url.full(url.encode())
    if position != len(url):
        raise ValueError(
            f"Invalid URL (at position: {position} - {url[position]!r}): "
            + url
        )

    match = get_matchs(match)

    function = handlers[match["scheme"][0].decode()]

    if function.__code__.co_flags & 0x80:
        return AsyncTask(function(match, **kwargs), True)

    return SyncTask(partial(function, match, **kwargs), False)


async def run_tasks(*urls: List[str]) -> List[Task]:
    """
    This function run tasks from URLs.
    """

    async_tasks = []
    threads = []
    tasks = []

    for url in urls:
        task = get_task(url)
        tasks.append(task)

        if task.is_awaitable:
            async_tasks.append(task.run())
        else:
            thread = Thread(target=task.run)
            threads.append(thread)
            thread.start()

    await gather(*async_tasks)
    [thread.join() for thread in threads]
    return tasks


def main() -> int:
    """
    This function is the main function to start the script
    from the command line.
    """

    responses = run(
        run_tasks(
            "http://127.0.0.1:8000/",
            "http://127.0.0.1:8000/1",
            "http://127.0.0.1:8000/2",
            "http+POST://test:test@127.0.0.1:8000/2;Filename=toto123?whynot#mydata",
            "script:test.py;test=test&test2=test?test=test#mydata",
            "https+GET+insecure://31.172.239.74/",
            "webscripts://127.0.0.1:8000/show_license.py?codeheader",
            "webscripts://127.0.0.1:8000/test_config.py?select=test&password=test&password=test&--test-date=2025-07-18&test_input=trololo&test_number=45#select%0aarguments%0a",
        )
    )

    for response in responses:
        print(response.code)

    return 0


handlers = {
    "http": handle_http,
    "https": handle_http,
    "http+POST": handle_method_http_body,
    "https+POST": handle_method_http_body,
    "https+POST+insecure": handle_method_http_body,
    "http+PUT": handle_method_http_body,
    "https+PUT": handle_method_http_body,
    "https+PUT+insecure": handle_method_http_body,
    "http+GET": handle_method_http_body,
    "https+GET": handle_method_http_body,
    "https+GET+insecure": handle_method_http_body,
    "http+DELETE": handle_method_http_body,
    "https+DELETE": handle_method_http_body,
    "https+DELETE+insecure": handle_method_http_body,
    "http+HEAD": handle_method_http_body,
    "https+HEAD": handle_method_http_body,
    "https+HEAD+insecure": handle_method_http_body,
    "http+TRACE": handle_method_http_body,
    "https+TRACE+insecure": handle_method_http_body,
    "http+OPTIONS": handle_method_http_body,
    "https+OPTIONS+insecure": handle_method_http_body,
    "http+CONNECT": handle_method_http_body,
    "https+CONNECT": handle_method_http_body,
    "https+CONNECT+insecure": handle_method_http_body,
    "http+PATCH": handle_method_http_body,
    "https+PATCH": handle_method_http_body,
    "https+PATCH+insecure": handle_method_http_body,
    "webscripts": handle_webscripts,
    "webscriptss": handle_webscripts,
    "webscriptss+insecure": handle_webscripts,
    "exe": handle_executable,
    "executable": handle_executable,
    "python": handle_python,
    "script": handle_python,
    "pyscript": handle_python,
}


if __name__ == "__main__":
    exit(main())
