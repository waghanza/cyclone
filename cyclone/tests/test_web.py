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
from cyclone.web import RequestHandler, HTTPError
from cyclone.web import Application
from cyclone.escape import unicode_type
from mock import Mock
from datetime import datetime


class RequestHandlerTest(unittest.TestCase):
    def assertHasAttr(self, obj, attr_name):
        assert hasattr(obj, attr_name)

    def setUp(self):
        self.app = Application(some_setting="foo")
        self.request = Mock()
        self.rh = RequestHandler(self.app, self.request)

    def test_init(self):
        self.assertHasAttr(self.rh, "application")
        self.assertHasAttr(self.rh, "request")
        self.assertHasAttr(self.rh, "path_args")
        self.assertHasAttr(self.rh, "path_kwargs")
        self.assertHasAttr(self.rh, "ui")

    def test_settings(self):
        self.assertEqual(self.rh.settings, {"some_setting": "foo"})

    def test_default(self):
        self.assertRaises(HTTPError, self.rh.default)

    def test_prepare(self):
        self.assertIsNone(self.rh.prepare())

    def test_on_finish(self):
        self.assertIsNone(self.rh.on_finish())

    def test_on_connection_close(self):
        self.assertIsNone(self.rh.on_connection_close())

    def test_clear(self):
        self.request.headers = {
            "Connection": "Keep-Alive"
        }
        self.request.supports_http_1_1.return_value = False
        self.rh.clear()
        self.assertEqual(
            set(self.rh._headers.keys()),
            set(["Server", "Content-Type", "Date", "Connection"])
        )
        self.assertEqual(self.rh._list_headers, [])

    def test_set_status(self):
        self.rh.set_status(200)
        self.assertEqual(self.rh._status_code, 200)

    def test_set_status_with_reason(self):
        self.rh.set_status(200, "reason")
        self.assertEqual(self.rh._status_code, 200)
        self.assertEqual(self.rh._reason, "reason")

    def test_set_status_with_invalid_code(self):
        self.assertRaises(ValueError, self.rh.set_status, 9999)

    def test_get_status(self):
        self.rh.set_status(200)
        self.assertEqual(self.rh.get_status(), 200)

    def test_add_header(self):
        self.rh.add_header("X-Header", "something")
        self.assertEqual(
            self.rh._list_headers,
            [("X-Header", "something")]
        )
        self.rh.add_header("X-Header", "something")
        self.assertEqual(
            self.rh._list_headers,
            [("X-Header", "something"), ("X-Header", "something")]
        )

    def test_clear_header(self):
        self.rh.set_header("X-Header", "something")
        self.assertTrue("X-Header" in self.rh._headers)
        self.rh.clear_header("X-Header")
        self.assertTrue("X-Header" not in self.rh._headers)

    def test_convert_header_value(self):
        value = self.rh._convert_header_value("Value")
        self.assertEqual(value, "Value")

    def test_convert_unicode_header_value(self):
        value = self.rh._convert_header_value(u"Value")
        self.assertEqual(value, "Value")
        self.assertTrue(type(value) != unicode_type)

    def test_convert_unicode_datetime_header_value(self):
        now = datetime(2014, 4, 4)
        result = self.rh._convert_header_value(now)
        self.assertEqual(
            result,
            "Fri, 04 Apr 2014 00:00:00 GMT"
        )

    def test_convert_invalid_value(self):

        class Nothing:
            pass

        self.assertRaises(TypeError, self.rh._convert_header_value, Nothing())

    def test_convert_long_value(self):
        self.assertRaises(
            ValueError, self.rh._convert_header_value, "a" * 5000)

    def test_get_argument(self):
        self.rh.get_arguments = Mock()
        self.rh.get_arguments.return_value = ["a"]
        self.rh.get_argument("test")
        self.rh.get_arguments.assert_called_with("test", strip=True)

