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

import cyclone.web
import functools
import sys

from twisted.python import log
from twisted.internet import reactor

__handlers = []

class Router:
    def __init__(self):
        self.items = []

    def add(self, method, callback):
        self.items.append((method, callback))

    def __call__(self, *args, **kwargs):
        obj = cyclone.web.RequestHandler(*args, **kwargs)
        for (method, callback) in self.items:
            callback = functools.partial(callback, obj)
            setattr(obj, method.lower(), callback)
        return obj

def route(path=None, method="GET", callback=None, **kwargs):
    if callable(path):
        path, callback = None, path

    def decorator(callback):
        __handlers.append((path, method, callback, kwargs))
        return callback

    return decorator


def run(**settings):
    handlers = {}
    for (path, method, callback, kwargs) in __handlers:
        if path not in handlers:
            handlers[path] = Router()
        handlers[path].add(method, callback)

    log.startLogging(settings.get("log", sys.stdout))
    application = cyclone.web.Application(handlers.items(), **settings)
    port = settings.get("port", 8888)
    interface = settings.get("host", "127.0.0.1")
    reactor.listenTCP(port, application, interface=interface)
    reactor.run()
