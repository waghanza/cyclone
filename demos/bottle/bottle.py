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

import sys
import cyclone.sqlite
from cyclone.bottle import run, route

@route("/")
def index(web):
    web.write("try /sqlite\r\n")

@route("/sqlite")
def sqlite_get(web):
    v = web.settings.sqlite.runQuery("select strftime('%Y-%m-%d')")
    web.write("today is " + repr(v) + "\r\n")

run(host="127.0.0.1", port=8080,
    log=sys.stdout, # or any file descriptor
    static_path="static", template_path="template",
    sqlite=cyclone.sqlite.InlineSQLite(":memory:"))

