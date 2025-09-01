# Copyright 2019 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import http.client
import queue
import socket
import ssl
import threading

import v3io.dataplane.request
import v3io.dataplane.response

from . import abstract

_connection_timeout_seconds = 20
_request_max_retries = 2


class Transport(abstract.Transport):

    def __init__(self, logger, endpoint=None, max_connections=None, timeout=None, verbosity=None):
        super(Transport, self).__init__(logger, endpoint, max_connections, timeout, verbosity)

        self._free_connections = queue.Queue()

        # based on scheme, create a host and context for _create_connection
        self._host, self._ssl_context = self._parse_endpoint(self._endpoint)
        self._ssl_context_lock = threading.Lock()

        # create the pool connection
        self._create_connections(self.max_connections, self._host, self._ssl_context)

        self._send_request_exceptions = (
            BrokenPipeError,
            http.client.CannotSendRequest,
            http.client.RemoteDisconnected,
            socket.timeout,
            ssl.SSLError,
        )
        self._get_status_and_headers = self._get_status_and_headers_py3

    @classmethod
    def get_connection_timeout(cls):
        global _connection_timeout_seconds
        return _connection_timeout_seconds

    @classmethod
    def set_connection_timeout(cls, timeout):
        global _connection_timeout_seconds
        _connection_timeout_seconds = timeout

    @classmethod
    def set_request_max_retries(cls, retries):
        global _request_max_retries
        _request_max_retries = retries

    @classmethod
    def get_request_max_retries(cls):
        global _request_max_retries
        return _request_max_retries

    def close(self):
        # Ignore redundant calls to close
        if not self._free_connections:
            return

        connections = []
        while not self._free_connections.empty():
            conn = self._free_connections.get()
            connections.append(conn)
        # In case anyone tries to reuse this object, we want them to get an error and not hang
        self._free_connections = None
        self._logger.debug(f"Closing all {len(connections)} v3io transport connections")
        for conn in connections:
            conn.close()

    def requires_access_key(self):
        return True

    def send_request(self, request):
        if not self._free_connections:
            raise RuntimeError("Cannot send request on a closed client")

        # TODO: consider getting param of whether we should block or
        #       not (wait for connection to be free or raise exception)
        connection = self._free_connections.get(block=True, timeout=None)

        try:
            return self._send_request_on_connection(request, connection)
        except BaseException as e:
            request.transport.connection_used.close()
            connection = self._create_connection(self._host, self._ssl_context)
            self._free_connections.put(connection, block=True)
            raise e

    def wait_response(self, request, raise_for_status=None, num_retries=1):
        connection = request.transport.connection_used
        is_retry = False

        while True:
            response_body = None
            status_code = None
            headers = None
            try:
                if is_retry:
                    request = self._send_request_on_connection(request, connection)
                    connection = request.transport.connection_used

                response = connection.getresponse()
                response_body = response.read()

                status_code, headers = self._get_status_and_headers(response)

                self.log("Rx", connection=connection, status_code=status_code, body=response_body)

                response = v3io.dataplane.response.Response(request.output, status_code, headers, response_body)

                self._free_connections.put(connection, block=True)

                response.raise_for_status(request.raise_for_status or raise_for_status)

                return response

            except v3io.dataplane.response.HttpResponseError as response_error:
                self._logger.warn_with(f"Response error: {response_error}")
                raise response_error
            except BaseException as e:
                connection.close()
                connection = self._create_connection(self._host, self._ssl_context)

                if num_retries == 0:
                    self._logger.error_with(
                        "Error occurred while waiting for response and ran out of retries",
                        e=type(e),
                        e_msg=e,
                        response_body=response_body,
                        status_code=status_code,
                        headers=headers,
                    )
                    self._free_connections.put(connection, block=True)
                    raise e

                self._logger.debug_with(
                    "Error occurred while waiting for response – retrying",
                    retries_left=num_retries,
                    e=type(e),
                    e_msg=e,
                )

            num_retries -= 1
            is_retry = True

    def _send_request_on_connection(self, request, connection):
        request.transport.connection_used = connection

        path = request.encode_path()

        self.log(
            "Tx", connection=connection, method=request.method, path=path, headers=request.headers, body=request.body
        )

        starting_offset = 0
        is_body_seekable = request.body and hasattr(request.body, "seek") and hasattr(request.body, "tell")
        if is_body_seekable:
            starting_offset = request.body.tell()

        retries_left = Transport.get_request_max_retries()
        while True:
            try:
                connection.request(request.method, path, request.body, request.headers)
                break
            except self._send_request_exceptions as e:
                self._logger.debug_with(
                    f"Disconnected while attempting to send request – "
                    f"{retries_left} out of {Transport.get_request_max_retries()} retries left.",
                    e=type(e),
                    e_msg=e,
                )
                if retries_left == 0:
                    raise
                retries_left -= 1
                connection.close()
                if is_body_seekable:
                    # If the first connection fails, the pointer of the body might move at the size
                    # of the first connection blocksize.
                    # We need to reset the position of the pointer in order to send the whole file.
                    request.body.seek(starting_offset)
                # ML-9894
                if isinstance(e, ssl.SSLError):
                    ssl_context_before_lock = self._ssl_context
                    # Only replace shared SSL context if it hasn't been replaced already due to the same error
                    # on another connection.
                    if ssl_context_before_lock is connection._context:
                        with self._ssl_context_lock:
                            # Only if it wasn't changed concurrently
                            if self._ssl_context is ssl_context_before_lock:
                                self._logger.info(f"Replacing SSL context due to SSLError: {e}")
                                self._ssl_context = self._create_ssl_context()
                connection = self._create_connection(self._host, self._ssl_context)
                request.transport.connection_used = connection
            except BaseException as e:
                self._logger.error_with(
                    "Unhandled exception while sending request", e=type(e), e_msg=e, connection=connection
                )
                raise e

        return request

    def _create_connections(self, num_connections, host, ssl_context):
        for _ in range(num_connections):
            connection = self._create_connection(host, ssl_context)
            self._free_connections.put(connection, block=True)

    def _create_connection(self, host, ssl_context):
        if ssl_context is None:
            return http.client.HTTPConnection(host, timeout=Transport.get_connection_timeout())

        return http.client.HTTPSConnection(host, timeout=Transport.get_connection_timeout(), context=ssl_context)

    def _create_ssl_context(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context

    def _parse_endpoint(self, endpoint):
        if endpoint.startswith("http://"):
            return endpoint[len("http://") :], None

        if endpoint.startswith("https://"):
            return endpoint[len("https://") :], self._create_ssl_context()

        return endpoint, None

    def _get_status_and_headers_py2(self, response):
        return response.status, response.getheaders()

    def _get_status_and_headers_py3(self, response):
        return response.code, response.headers
