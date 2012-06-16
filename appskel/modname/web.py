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

import cyclone.locale
import cyclone.web

from $modname import views
from $modname import config
from $modname.utils import DatabaseMixin


class Application(cyclone.web.Application):
    def __init__(self, config_file):
        handlers = [
            (r"/",              views.IndexHandler),
            (r"/lang/(.+)",     views.LangHandler),
            (r"/sample/mysql",  views.SampleMySQLHandler),
            (r"/sample/redis",  views.SampleRedisHandler),
            (r"/sample/sqlite", views.SampleSQLiteHandler),
        ]

        settings = config.parse_config(config_file)

        # Initialize locales
        locales = settings.get("locale_path")
        if locales:
            cyclone.locale.load_gettext_translations(locales, "$modname")

        # Set up database connections
        DatabaseMixin.setup(settings)

        #settings["login_url"] = "/auth/login"
        #settings["autoescape"] = None
        cyclone.web.Application.__init__(self, handlers, **settings)
