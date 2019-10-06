from twisted.trial import unittest

from cyclone.httputil import HTTPHeaders


class TestHTTPHeaders(unittest.TestCase):
    def test_parse_no_cr(self):
        """
        https://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.3
        "The line terminator for message-header fields is the sequence CRLF.
         However, we recommend that applications, when parsing such headers,
         recognize a single LF as a line terminator and ignore the leading CR."

	https://tools.ietf.org/html/rfc7230#section-3.5
        "Although the line terminator for the start-line and header fields is
         the sequence CRLF, a recipient MAY recognize a single LF as a line
         terminator and ignore any preceding CR."
        """
        header_data = u"Foo: bar\n" u"Baz: qux"
        headers = HTTPHeaders.parse(header_data)
        self.assertEqual(len(list(headers.get_all())), 2)
        self.assertEqual(headers.get("foo"), "bar")
        self.assertEqual(headers.get("baz"), "qux")

    def test_parse_crlf(self):
        """
        https://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.3
        "The line terminator for message-header fields is the sequence CRLF.
         However, we recommend that applications, when parsing such headers,
         recognize a single LF as a line terminator and ignore the leading CR."
        """
        header_data = u"Foo: bar\r\n" u"Baz: qux"
        headers = HTTPHeaders.parse(header_data)
        self.assertEqual(len(list(headers.get_all())), 2)
        self.assertEqual(headers.get("foo"), "bar")
        self.assertEqual(headers.get("baz"), "qux")

    def test_parse_problematic_newlines(self):
        """
        There are some problematic characters that Python considers to be newlines
        for the purpose of splitlines, but aren't newlines per the RFCs.

        https://docs.python.org/3/library/stdtypes.html#str.splitlines
        """
        header_data = (
            u"Foo: bar\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029asdf: jkl\r\n" u"Baz: qux"
        )
        headers = HTTPHeaders.parse(header_data)
        self.assertEqual(len(list(headers.get_all())), 2)
        self.assertEqual(
            headers.get("foo"), u"bar\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029asdf: jkl"
        )
        self.assertEqual(headers.get("baz"), "qux")
