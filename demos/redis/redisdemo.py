#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2010 Alexandre Fiori
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

import collections
import os.path
import sys


import cyclone.web
import cyclone.redis
from cyclone.redis.protocol import SubscriberProtocol

from twisted.python import log
from twisted.internet import defer, reactor

class Application(cyclone.web.Application):
    def __init__(self):
        redis_host = "127.0.0.1"
        redis_port = 6379

        # PubSub connection
        queue = QueueFactory()
        reactor.connectTCP(redis_host, redis_port, queue)

        # Normal client connection
        redisdb = cyclone.redis.lazyRedisConnectionPool(redis_host, redis_port,
                                                        pool_size=10, db=0)

        handlers = [
            (r"/text/(.+)", TextHandler, dict(redisdb=redisdb)),
            (r"/queue/(.+)", QueueHandler, dict(queue=queue, redisdb=redisdb)),
        ]
        settings = dict(
            static_path="./frontend/static",
            template_path="./frontend/template",
        )
        cyclone.web.Application.__init__(self, handlers, **settings)


class TextHandler(cyclone.web.RequestHandler):
    def initialize(self, redisdb):
        self.redisdb = redisdb

    @defer.inlineCallbacks
    def get(self, key):
        try:
            value = yield self.redisdb.get(key)
        except Exception, e:
            log.err("Redis failed to get('%s'): %s" % (key, str(e)))
            raise cyclone.web.HTTPError(503)

        self.set_header("Content-Type", "text/plain")
        self.finish("%s=%s\r\n" % (key, value))

    @defer.inlineCallbacks
    def post(self, key):
        value = self.get_argument("value")
        try:
            yield self.redisdb.set(key, value)
        except Exception, e:
            log.err("Redis failed to set('%s', '%s'): %s" % (key, value, str(e)))
            raise cyclone.web.HTTPError(503)

        self.set_header("Content-Type", "text/plain")
        self.finish("%s=%s\r\n" % (key, value))

    @defer.inlineCallbacks
    def delete(self, key):
        try:
            n = yield self.redisdb.delete(key)
        except Exception, e:
            log.err("Redis failed to del('%s'): %s" % (key, str(e)))
            raise cyclone.web.HTTPError(503)

        self.set_header("Content-Type", "text/plain")
        self.finish("DEL %s=%d\r\n" % (key, n))


class QueueHandler(cyclone.web.RequestHandler):
    def initialize(self, queue, redisdb):
        self.queue = queue
        self.redisdb = redisdb

    @cyclone.web.asynchronous
    def get(self, channels):
        try:
            channels = channels.split(",")
        except Exception, e:
            log.err("Could not split channel names: %s" % str(e))
            raise cyclone.web.HTTPError(400, str(e))

        self.set_header("Content-Type", "text/plain")
        self.notifyFinish().addCallback(self._unsubscribe_all)

        for channel in channels:
            self._subscribe(channel)

    @defer.inlineCallbacks
    def post(self, channel):
        message = self.get_argument("message")
        if self.queue.current_connection is None:
            raise cyclone.web.HTTPError(503)

        try:
            n = yield self.redisdb.publish(channel, message.encode("utf-8"))
        except Exception, e:
            log.err("Redis failed to publish('%', '%s'): %s" % \
                    (channel, repr(message), str(e)))
            raise cyclone.web.HTTPError(503)

        self.set_header("Content-Type", "text/plain")
        self.finish("OK %d\r\n" % n)

    def _subscribe(self, channel):
        if "*" in channel:
            self.queue.current_connection.psubscribe(channel)
        else:
            self.queue.current_connection.subscribe(channel)

        self.queue.peers[channel].append(self)
        self.write("subscribed to %s\r\n" % channel)
        self.flush()

    def _unsubscribe_all(self, ign):
        for chan, peers in self.queue.peers.iteritems():
            try:
                peers.pop(peers.index(self))
            except:
                pass
            else:
                if self.queue.current_connection is not None:
                    if "*" in chan:
                        self.queue.current_connection.punsubscribe(chan)
                    else:
                        self.queue.current_connection.unsubscribe(chan)


class QueueProtocol(SubscriberProtocol):
    def messageReceived(self, pattern, channel, message):
        if pattern:
            peers = self.factory.peers.get(pattern)
        else:
            peers = self.factory.peers.get(channel)

        # Broadcast the message to all peers in channel
        for peer in peers:
            # peer is an HTTP client, RequestHandler
            peer.write("%s: %s\r\n" % (channel, message))
            peer.flush()

    def connectionMade(self):
        # If we lost connection with Redis during operation, we
        # re-subscribe all peers once the connection is re-established.
        self.factory.current_connection = self
        for chan in self.factory.peers:
            if "*" in chan:
                self.psubscribe(chan)
            else:
                self.subscribe(chan)

    def connectionLost(self, reason):
        self.factory.current_connection = None


class QueueFactory(cyclone.redis.SubscriberFactory):
    maxDelay = 20
    continueTrying = True # Auto-reconnect
    protocol = QueueProtocol
    peers = collections.defaultdict(lambda: [])
    current_connection = None


def main():
    log.startLogging(sys.stdout)
    reactor.listenTCP(8888, Application(), interface="127.0.0.1")
    reactor.run()


if __name__ == "__main__":
    main()
