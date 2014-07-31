from twisted.trial import unittest
from cyclone.testing import CycloneTestCase, Client
from cyclone.web import Application, RequestHandler, asynchronous
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


class TestHandler(RequestHandler):
    def get(self):
        self.write("Something")


class DeferredTestHandler(RequestHandler):
    @asynchronous
    def get(self):
        self.write("Something...")
        reactor.callLater(0.1, self.do_something)

    def do_something(self):
        self.write("done!")
        self.finish()


def mock_app_builder():
    return Application([
        (r'/testing/', TestHandler),
        (r'/deferred_testing/', DeferredTestHandler)
    ])


class TestTestCase(unittest.TestCase):
    def test_create(self):
        case = CycloneTestCase(mock_app_builder)
        self.assertTrue(case._app)
        self.assertTrue(case.client)


class TestClient(unittest.TestCase):
    def setUp(self):
        self.app = mock_app_builder()
        self.client = Client(self.app)

    def test_create_client(self):
        app = mock_app_builder()
        client = Client(app)
        self.assertTrue(client.app)

    @inlineCallbacks
    def test_get_request(self):
        response = yield self.client.get("/testing/")
        self.assertEqual(response.content, "Something")
        self.assertTrue(len(response.headers) > 3)

    @inlineCallbacks
    def test_get_deferred_request(self):
        response = yield self.client.get("/deferred_testing/")
        self.assertEqual(response.content, "Something...done!")
        self.assertTrue(len(response.headers) > 3)
