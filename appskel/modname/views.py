# coding: utf-8
#
# Copyright 2012 Alexandre Fiori
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

import cyclone.escape
import cyclone.locale
import cyclone.web

from twisted.internet import defer
from twisted.python import log

from $modname.utils import BaseHandler
from $modname.utils import DatabaseMixin


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class LangHandler(BaseHandler):
    def get(self, lang_code):
        if lang_code in cyclone.locale.get_supported_locales():
            self.set_secure_cookie("lang", lang_code)

        self.redirect(self.request.headers.get("Referer",
                                               self.get_argument("next", "/")))


class SampleSQLiteHandler(BaseHandler, DatabaseMixin):
    def get(self):
        if self.sqlite:
            response = self.sqlite.runQuery("select strftime('%Y-%m-%d')")
            self.write({"response": response})
        else:
            self.write("SQLite is disabled\r\n")


class SampleRedisHandler(BaseHandler, DatabaseMixin):
    @defer.inlineCallbacks
    def get(self):
        if self.redis:
            try:
                response = yield self.redis.get("foo")
            except Exception, e:
                log.msg("Redis query failed: %s" % str(e))
                raise cyclone.web.HTTPError(503)  # Service Unavailable
            else:
                self.write({"response": response})
        else:
            self.write("Redis is disabled\r\n")


class SampleMySQLHandler(BaseHandler, DatabaseMixin):
    @defer.inlineCallbacks
    def get(self):
        if self.mysql:
            try:
                response = yield self.mysql.runQuery("select now()")
            except Exception, e:
                log.msg("MySQL query failed: %s" % str(e))
                raise cyclone.web.HTTPError(503)  # Service Unavailable
            else:
                self.write({"response": response})
        else:
            self.write("MySQL is disabled\r\n")
