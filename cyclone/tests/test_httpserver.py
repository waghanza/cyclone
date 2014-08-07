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
from cyclone.httpserver import HTTPConnection
from twisted.internet.defer import Deferred, inlineCallbacks


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
