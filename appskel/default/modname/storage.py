# coding: utf-8
#
$license


import cyclone.redis
try:
    sqlite_ok = True
    import cyclone.sqlite
except ImportError, sqlite_err:
    sqlite_ok = False

from twisted.enterprise import adbapi
from twisted.python import log


class DatabaseMixin(object):
    mysql = None
    redis = None
    sqlite = None

    @classmethod
    def setup(cls, conf):
        if "sqlite_settings" in conf:
            if sqlite_ok:
                DatabaseMixin.sqlite = \
                cyclone.sqlite.InlineSQLite(conf["sqlite_settings"].database)
            else:
                log.err("SQLite is currently disabled: %s" % sqlite_err)

        if "redis_settings" in conf:
            if conf["redis_settings"].get("unixsocket"):
                DatabaseMixin.redis = \
                cyclone.redis.lazyUnixConnectionPool(
                              conf["redis_settings"].unixsocket,
                              conf["redis_settings"].dbid,
                              conf["redis_settings"].poolsize)
            else:
                DatabaseMixin.redis = \
                cyclone.redis.lazyConnectionPool(
                              conf["redis_settings"].host,
                              conf["redis_settings"].port,
                              conf["redis_settings"].dbid,
                              conf["redis_settings"].poolsize)

        if "mysql_settings" in conf:
            DatabaseMixin.mysql = \
            adbapi.ConnectionPool("MySQLdb",
                                  host=conf["mysql_settings"].host,
                                  port=conf["mysql_settings"].port,
                                  db=conf["mysql_settings"].database,
                                  user=conf["mysql_settings"].username,
                                  passwd=conf["mysql_settings"].password,
                                  cp_min=1,
                                  cp_max=conf["mysql_settings"].poolsize,
                                  cp_reconnect=True,
                                  cp_noisy=conf["mysql_settings"].debug)
