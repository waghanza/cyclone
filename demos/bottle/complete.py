#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2011 Alexandre Fiori
# based on the original Tornado by Facebook
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
import cyclone.redis
import cyclone.sqlite
import cyclone.web
from cyclone.bottle import run, route
from twisted.internet import defer

class BaseHandler(cyclone.web.RequestHandler):
    def get_current_user(self):
        print "Getting user cookie"
        return self.get_secure_cookie("user")


@route("/")
def index(req):
    req.write("""try /sqlite, /redis or <a href="/auth/login">sign in</a>""")


@route("/auth/login")
def auth_login_page(req):
    req.write("""
    <html><body><form method="POST">
    username: <input type="text" name="user"/><br/>
    password: <input type="password" name="passwd"/><br/>
    <input type="submit">
    </form></body></html>
    """)

@route("/auth/login", method="POST")
def auth_login(req):
    user = req.get_argument("user")
    passwd = req.get_argument("passwd")
    next = req.get_argument("next", "/private")
    # assert user=="foo" and passwd=="bar"
    req.set_secure_cookie("user", user)
    req.redirect(next)

@route("/auth/logout")
@cyclone.web.authenticated
def auth_logout(req):
    req.clear_cookie("user")
    req.redirect("/")

@route("/private")
@cyclone.web.authenticated
def private(req):
    req.write("current user is: %s<br/>" % repr(req.current_user))
    req.write("""<a href="/auth/logout">logout</a>""")


@route("/sqlite")
def sqlite_get(req):
    v = req.settings.sqlite.runQuery("select strftime('%Y-%m-%d')")
    req.write("today is " + repr(v) + "\r\n")


@route("/redis")
@defer.inlineCallbacks
def redis_get(req):
    try:
        v = yield req.settings.redis.get("foo")
        req.write("foo = " + repr(v) + "\r\n")
    except:
        raise cyclone.web.HTTPError(503)

@route("/redis", method="POST")
@defer.inlineCallbacks
def redis_set(req):
    try:
        foo = req.get_argument("foo", "null")
        yield req.settings.redis.set("foo", foo)
        req.write("OK\r\n")
    except:
        raise cyclone.web.HTTPError(503)


class WebSocketHandler(cyclone.web.WebSocketHandler):
    def connectionMade(self, *args, **kwargs):
        print "connection made:", args, kwargs

    def messageReceived(self, message):
        self.sendMessage("echo: %s" % message)

    def connectionLost(self, why):
        print "connection lost:", why


class XmlrpcHandler(cyclone.web.XmlrpcRequestHandler):
    allowNone = True

    def xmlrpc_echo(self, text):
        return text


try:
    raise COMMENT_THIS_LINE_AND_LOG_TO_DAILY_FILE
    from twisted.python.logfile import DailyLogFile
    logFile = DailyLogFile.fromFullPath("server.log")
    print("Logging to daily log file: server.log")
except Exception, e:
    import sys
    logFile = sys.stdout

run(host="127.0.0.1", port=8080,
    log=logFile,
    static_path="static",
    template_path="template",
    locale_path="locale",
    sqlite=cyclone.sqlite.InlineSQLite(":memory:"),
    redis=cyclone.redis.lazyRedisConnectionPool(),
    base_handler=BaseHandler,
    cookie_secret="32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url="/auth/login",
    more_handlers=[
        (r"/websocket",    WebSocketHandler),
        (r"/xmlrpc",       XmlrpcHandler),
    ])

