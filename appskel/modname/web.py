# coding: utf-8
#
$license

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
