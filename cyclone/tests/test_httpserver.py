#
# Copyright 2014 David Novakovic
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

from twisted.trial import unittest
from mock import Mock
from cyclone.httpserver import HTTPConnection, _BadRequestException
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.test.proto_helpers import StringTransport
from io import BytesIO


class HTTPConnectionTest(unittest.TestCase):
    def setUp(self):
        self.con = HTTPConnection()
        self.con.factory = Mock()

    def test_connectionMade(self):
        self.con.factory.settings.get.return_value = None
        self.con.connectionMade()
        self.assertTrue(hasattr(self.con, "no_keep_alive"))
        self.assertTrue(hasattr(self.con, "content_length"))
        self.assertTrue(hasattr(self.con, "xheaders"))

    def test_connectionLost(self):
        m = Mock()
        reason = Mock()
        reason.getErrorMessage.return_value = "Some message"
        self.con._finish_callback = Deferred().addCallback(m)
        self.con.connectionLost(reason)
        m.assert_called_with("Some message")

    def test_notifyFinish(self):
        self.con.connectionMade()
        d = self.con.notifyFinish()
        self.assertIsInstance(d, Deferred)

    def test_lineReceived(self):
        self.con.connectionMade()
        line = "Header: something"
        self.con.lineReceived(line)
        self.assertTrue(line + self.con.delimiter in self.con._headersbuffer)
        self.con._on_headers = Mock()
        self.con.lineReceived("")
        self.con._on_headers.assert_called_with('Header: something\r\n')

    def test_rawDataReceived(self):
        self.con.connectionMade()
        self.con._contentbuffer = BytesIO()
        self.con._on_request_body = Mock()
        self.con.content_length = 5
        data = "some data"
        self.con.rawDataReceived(data)
        self.con._on_request_body.assert_called_with("some ")

    def test_write(self):
        self.con.transport = StringTransport()
        self.con._request = Mock()
        self.con.write("data")
        self.assertEqual(self.con.transport.io.getvalue(), "data")

    def test_finish(self):
        self.con._request = Mock()
        self.con._finish_request = Mock()
        self.con.finish()
        self.con._finish_request.assert_called_with()
        self.assertTrue(self.con._request_finished)

    def test_on_write_complete(self):
        self.con._request_finished = True
        self.con._finish_request = Mock()
        self.con._on_write_complete()
        self.con._finish_request.assert_called_with()

    def test_finish_request_close(self):
        self.con.connectionMade()
        self.con.transport = Mock()
        self.con._request = Mock()
        self.con._request.headers.get.return_value = "close"
        self.con._finish_request()
        self.con.transport.loseConnection.assert_called_with()

    def test_finish_request_no_keep_alive(self):
        self.con.connectionMade()
        self.con.transport = Mock()
        self.con._request = Mock()
        self.con._request.headers = {
            "Content-Length": "1",
            "Connection": "close"
        }
        self.con._request.supports_http_1_1.return_value = False
        self.con._finish_request()
        self.con.transport.loseConnection.assert_called_with()

    def test_finish_request_no_keep_alive_setting(self):
        self.con.connectionMade()
        self.con.no_keep_alive = True
        self.con.transport = Mock()
        self.con._request = Mock()
        self.con._finish_request()
        self.con.transport.loseConnection.assert_called_with()

    def test_finish_request_head(self):
        self.con.connectionMade()
        self.con.transport = Mock()
        self.con._request = Mock()
        self.con._request.method = "HEAD"
        self.con._request.headers = {
            "Connection": "close"
        }
        self.con._request.supports_http_1_1.return_value = False
        self.con._finish_request()
        self.con.transport.loseConnection.assert_called_with()

    def test_finish_request_http1_discon(self):
        self.con.connectionMade()
        self.con.transport = Mock()
        self.con._request = Mock()
        self.con._request.method = "POST"
        self.con._request.headers = {
            "Connection": "Keep-Alive"
        }
        self.con._request.supports_http_1_1.return_value = False
        self.con._finish_request()
        self.con.transport.loseConnection.assert_called_with()

    def test_on_headers_simple(self):
        self.con._remote_ip = Mock()
        self.con.request_callback = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET / HTTP/1.1\r\n"
        self.con._on_headers(data)
        self.assertEqual(self.con.request_callback.call_count, 1)

    def test_on_headers_invalid(self):
        self.con._remote_ip = Mock()
        self.con.request_callback = Mock()
        self.con.transport = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET /"
        self.con._on_headers(data)
        self.con.transport.loseConnection.assert_called_with()

    def test_on_headers_invalid_version(self):
        self.con._remote_ip = Mock()
        self.con.request_callback = Mock()
        self.con.transport = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET / HTTS/1.1"
        self.con._on_headers(data)
        self.con.transport.loseConnection.assert_called_with()

    def test_on_headers_content_length(self):
        self.con._remote_ip = Mock()
        self.con.setRawMode = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET / HTTP/1.1\r\n"\
            "Content-Length: 5\r\n"\
            "\r\n"
        self.con._on_headers(data)
        self.con.setRawMode.assert_called_with()
        self.assertEqual(self.con.content_length, 5)

    def test_on_headers_continue(self):
        self.con._remote_ip = Mock()
        self.con.transport = StringTransport()
        self.con.setRawMode = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET / HTTP/1.1\r\n"\
            "Content-Length: 5\r\n"\
            "Expect: 100-continue"\
            "\r\n"
        self.con._on_headers(data)
        self.assertEqual(
            self.con.transport.io.getvalue().strip(),
            "HTTP/1.1 100 (Continue)"
        )


    def test_on_headers_big_body(self):
        self.con._remote_ip = Mock()
        self.con.transport = StringTransport()
        self.con.setRawMode = Mock()
        self.con.__dict__['_remote_ip'] = "127.0.0.1"
        self.con.connectionMade()
        data = \
            "GET / HTTP/1.1\r\n"\
            "Content-Length: 10000000\r\n"\
            "\r\n"
        self.con._on_headers(data)
        self.assertTrue(self.con._contentbuffer)

    # def _on_request_body()
