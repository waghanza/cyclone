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

import sys

from twisted.application import internet
from twisted.application import service
from twisted.internet import ssl
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.python import reflect
from zope.interface import implements


class Options(usage.Options):
    optParameters = [
        ["port", "p", 8888, "tcp port to listen on", int],
        ["listen", "l", "127.0.0.1", "interface to listen on"],
        ["app", "r", None, "cyclone application to run"],
        ["appopts", None, None, "arguments to your application"],
        ["sslport", None, 8443, "port to listen on for ssl", int],
        ["ssliface", None, "127.0.0.1", "interface to listen on for ssl"],
        ["sslcert", None, "server.crt", "ssl certificate"],
        ["sslkey", None, "server.key", "ssl server key"],
        ["sslapp", None, None, "ssl application (same as --app)"],
        ["sslappopts", None, None, "arguments to the ssl application"],
    ]


class ServiceMaker(object):
    implements(service.IServiceMaker, IPlugin)
    tapname = "cyclone"
    description = "cyclone web server"
    options = Options

    def makeService(self, options):
        srv = service.MultiService()
        s = None

        # http
        if options["app"]:
            appmod = reflect.namedAny(options["app"])
            if options["appopts"]:
                app = appmod(options["appopts"])
            else:
                app = appmod()
            s = internet.TCPServer(options["port"], app,
                                   interface=options["listen"])
            s.setServiceParent(srv)

        # https
        if options["sslapp"]:
            appmod = reflect.namedAny(options["sslapp"])
            if options["sslappopts"]:
                app = appmod(options["sslappopts"])
            else:
                app = appmod()
            s = internet.SSLServer(options["sslport"], app,
                                   ssl.DefaultOpenSSLContextFactory(
                                   options["sslkey"], options["sslcert"]),
                                   interface=options["ssliface"])
            s.setServiceParent(srv)

        if s is None:
            print("Nothing to do. Try --help")
            sys.exit(1)

        return srv

serviceMaker = ServiceMaker()
