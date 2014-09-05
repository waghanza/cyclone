from twisted.trial import unittest
from twisted.internet import defer, reactor
from mock import Mock

from cyclone import web
from cyclone.template import DictLoader

class TestRequestHandler(unittest.TestCase):

    @defer.inlineCallbacks
    def test_render_string(self):
        _mkDeferred = self._mkDeferred
        self.assertEqual(
            self.handler.render_string("simple.html", msg="Hello World!"),
            "simple: Hello World!"
        )
        self.assertEqual(
            self.handler.render_string("simple.html", msg=_mkDeferred("Hello Deferred!")),
            "simple: Hello Deferred!"
        )
        d = self.handler.render_string("simple.html", msg=_mkDeferred("Hello Deferred!", 0.1))
        self.assertTrue(isinstance(d, defer.Deferred), d)
        msg = yield d
        self.assertEqual(msg, "simple: Hello Deferred!")

    def test_generate_headers(self):
        headers = self.handler._generate_headers()
        self.assertIn(
            "HTTP MOCK 200 OK",
            headers,
        )

    @defer.inlineCallbacks
    def test_simple_handler(self):
        self.handler.get = lambda: self.handler.finish("HELLO WORLD")
        page = yield self._execute_request(False)
        self.assertEqual(page, "HELLO WORLD")

    @defer.inlineCallbacks
    def test_deferred_handler(self):
        self.handler.get = lambda: self._mkDeferred(lambda: self.handler.finish("HELLO DEFERRED"), 0.01)
        page = yield self._execute_request(False)
        self.assertEqual(page, "HELLO DEFERRED")

    @defer.inlineCallbacks
    def test_deferred_arg_in_render(self):
        templateArg = self._mkDeferred("it works!", 0.1)
        handlerGetFn = lambda: self.handler.render("simple.html", msg=templateArg)
        self.handler.get = handlerGetFn
        page = yield self._execute_request(False)
        self.assertEqual(page, "simple: it works!")

    def setUp(self):
        self.app = app = Mock()
        app.ui_methods = {}
        app.ui_modules = {}
        app.settings = {
            "template_loader": DictLoader({
                "simple.html": "simple: {{msg}}",
            }),
        }

        self.request = request = Mock()
        request.headers = {}
        request.method = "GET"
        request.version = "HTTP MOCK"
        request.notifyFinish.return_value = defer.Deferred()
        request.supports_http_1_1.return_value = True

        self.handler = web.RequestHandler(app, request)
        self._onFinishD = defer.Deferred()

        origFinish = self.handler.on_finish
        self.handler.on_finish = lambda: (
            origFinish(),
            self._onFinishD.callback(None),
        )

    def _mkDeferred(self, rv, delay=None):
        d = defer.Deferred()

        if callable(rv):
            cb = lambda: d.callback(rv())
        else:
            cb = lambda: d.callback(rv)

        if delay is None:
            cb()
        else:
            reactor.callLater(delay, cb)
        return d

    @defer.inlineCallbacks
    def _execute_request(self, outputHeaders):
        handler = self.handler

        handler._headers_written = True
        handler._execute([])
        yield self._onFinishD

        out = ""
        for (args, kwargs) in self.request.write.call_args_list:
            self.assertFalse(kwargs)
            self.assertEqual(len(args), 1)
            out += args[0]
        defer.returnValue(out)