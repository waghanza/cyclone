#
# Copyright 2010 David Novakovic
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cyclone.httpserver import HTTPRequest, HTTPConnection
import urllib
from twisted.test import proto_helpers
from twisted.internet.defer import inlineCallbacks, returnValue


class Client(object):
    def __init__(self, app):
        self.app = app

    def get(self, uri, params=None, version="HTTP/1.0", headers=None,
            body=None, remote_ip=None, protocol=None, host=None,
            files=None, connection=None):
        return self.request(
            "GET", uri, params=params, version=version, headers=headers,
            body=body, remote_ip=remote_ip, protocol=protocol, host=host,
            files=files, connection=connection
        )

    def put(self, uri, params=None, version="HTTP/1.0", headers=None,
            body=None, remote_ip=None, protocol=None, host=None,
            files=None, connection=None):
        return self.request(
            "PUT", uri, params=params, version=version, headers=headers,
            body=body, remote_ip=remote_ip, protocol=protocol, host=host,
            files=files, connection=connection
        )

    def post(self, uri, params=None, version="HTTP/1.0", headers=None,
             body=None, remote_ip=None, protocol=None, host=None,
             files=None, connection=None):
        return self.request(
            "POST", uri, params=params, version=version, headers=headers,
            body=body, remote_ip=remote_ip, protocol=protocol, host=host,
            files=files, connection=connection
        )

    def delete(self, uri, params=None, version="HTTP/1.0", headers=None,
               body=None, remote_ip=None, protocol=None, host=None,
               files=None, connection=None):
        return self.request(
            "DELETE", uri, params=params, version=version, headers=headers,
            body=body, remote_ip=remote_ip, protocol=protocol, host=host,
            files=files, connection=connection
        )

    def head(self, uri, params=None, version="HTTP/1.0", headers=None,
             body=None, remote_ip=None, protocol=None, host=None,
             files=None, connection=None):
        return self.request(
            "HEAD", uri, params=params, version=version, headers=headers,
            body=body, remote_ip=remote_ip, protocol=protocol, host=host,
            files=files, connection=connection
        )

    @inlineCallbacks
    def request(self, method, uri, *args, **kwargs):
        params = kwargs.pop("params")
        if params:
            uri = uri + "?" + urllib.urlencode(params)
        connection = kwargs.pop('connection')
        if not connection:
            connection = HTTPConnection()
            connection.xheaders = False
            kwargs['connection'] = connection
        connection.factory = self.app

        request = HTTPRequest(method, uri, *args, **kwargs)
        connection.connectionMade()
        connection._request = request
        connection.transport = proto_helpers.StringTransport()
        request.remote_ip = connection.transport.getHost().host
        handler = self.app(request)

        def setup_response():
            response_body = connection.transport.io.getvalue()
            handler.content = response_body.split("\r\n\r\n", 1)[1]
            handler.headers = handler._headers

        if handler._finished:
            setup_response()
            returnValue(handler)
        yield connection.notifyFinish()
        setup_response()
        returnValue(handler)
