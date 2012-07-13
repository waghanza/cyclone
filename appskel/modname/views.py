# coding: utf-8
#
$license

import cyclone.escape
import cyclone.locale
import cyclone.web

from twisted.internet import defer
from twisted.python import log

from $modname.utils import BaseHandler
from $modname.utils import DatabaseMixin


class TemplateFields(dict):
    """Helper class to make sure our
        template doesn't fail due to an invalid key"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self[name] = value


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html", hello='world', awesome='bacon')
        # another option would be
        # fields = {'hello': 'world', 'awesome': 'bacon'}
        # self.render('index.html', **fields)

    def post(self):
        tpl_fields = TemplateFields()
        tpl_fields['post'] = True
        tpl_fields['ip'] = self.request.remote_ip
        self.render("post.html", fields=tpl_fields)


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
