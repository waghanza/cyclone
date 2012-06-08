=======
cyclone
=======
:Info: See `github <http://github.com/fiorix/cyclone>`_ for the latest source.
:Author: Alexandre Fiori <fiorix@gmail.com>

About
=====

cyclone is a clone of facebook's `Tornado <http://tornadoweb.org>`_, on top of
`Twisted <http://twistedmatrix.com>`_.

The web framework is very similar, but cyclone leverages all enterprise class
features of Twisted, and more.

It is extremely stable, and ready for production.


Features
--------

**cyclone is a Twisted protocol**. Thus, it may be used in conjunction with
any other protocol implemented in Twisted. The same server can deliver HTTP
content on one port, SSH on another, and it can keep a pool of persistent,
non-blocking connections to several databases. All in a single process.

Web apps built with cyclone are **fully translatable**. The localisation system
is based on `Gettext <http://www.gnu.org/software/gettext/>`_. It's possible
to translate strings in the server code, as well as text and HTML templates.

**Secure**. It can deliver HTTP and **HTTPS (SSL)** on the same server, with
individual request routing mechanism. Also, cyclone supports the standard HTTP
Authentication, which can be used to implement HTTP Basic, Digest, or any
other hand crafted authentication system, like `Amazon's S3
<http://docs.amazonwebservices.com/AmazonS3/latest/dev/RESTAuthentication.html>`_.

**API friendly**. cyclone is very useful for writing web APIs, RESTful or not.
Features like HTTP Keep-Alive and XSRF can be enabled or disabled per request,
which means the server can have different behaviour when communicating with
browsers, or other custom HTTP clients.

Ships with a full featured, **non-blocking HTTP client**, using
`TwistedWeb <http://twistedmatrix.com/trac/wiki/TwistedWeb>`_.

**E-mail, the easy way**. With cyclone, the web server can connect to multiple
SMTP servers, on demand. The e-mail API is simple, support client connections
with SSL and TLS, and provide you with an easy way to customize messages,
and attachments.

Supports **multiple protocols**: built-in support for XML-RPC, JSON-RPC,
WebSocket and SSE. And, many other protocols can be used in cyclone-based web
servers, like the `Event Socket <http://wiki.freeswitch.org/wiki/Event_Socket>`_
protocol of `Freeswitch <http://freeswitch.org/>`_, a highly scalable soft
switch, telephony platform.

**Storage engines**: cyclone ships with built-in support for inline SQLite,
and `Redis <http://redis.io/>`_. MongoDB and many other NoSQL are supported
with 3rd party libraries. All other RDBMs supported by Python are available as
well, like MySQL and PostgreSQL, via `twisted.enterprise.adbapi
<http://twistedmatrix.com/documents/current/core/howto/rdbms.html>`_.
Connection pools can persist, and be efficiently used by all requests. It can
also auto-reconnect automatically, making it totally fault-tolerant on database
errors and disconnections.

**For the simple, and the complex**: cyclone-based web apps can be written as
`Bottle <http://bottlepy.org/>`_, or Tornado. A 10-line script can handle
thousands of connections per second, with very low CPU and memory footprint.
For more complex applications, cyclone offers an app template out of the box,
with a configuration file, database support, translation, and deployment
scheme, fully integrated with Debian GNU/Linux. Via ``twistd``, cyclone-based
apps can be easily deployed in any operating system, with customized log and
pid files, reactor, permissions, and many other settings.

**Documented**, here and there, mostly by sample code. Features are either
documented here, or in the demos. Check out `the demos
<https://github.com/fiorix/cyclone/tree/master/demos>`_.
For some other stuff, we use the Tornado docs. Like `HTML templates
<http://www.tornadoweb.org/documentation/template.html>`_, `Escaping and
string manipulation <http://www.tornadoweb.org/documentation/escape.html>`_,
`Locale <http://www.tornadoweb.org/documentation/locale.html>`_, and
`OpenID and Oauth <http://www.tornadoweb.org/documentation/auth.html>`_.


Benchmarks
----------

Check out the `benchmarks <http://wiki.github.com/fiorix/cyclone/benchmarks>`_ page.


Development and Deployment
==========================

Twisted Plugin is the recommended way to go for production. Create new projects
right away off of the generic application skeleton shipped with cyclone::

    $ python -m cyclone.app --help

    use: cyclone/app.py [options]
    Options:
    -h --help              Show this help.
    -g --git               Use git's name and email settings, and create a git repo on target
    -p --project=NAME      Create new cyclone project.
    -m --modname=NAME      Use another name for the module [default: project_name]
    -v --version=VERSION   Set project version [default: 0.1]
    -s --set-pkg-version   Set version on package name [default: False]
    -t --target=PATH       Set path where project is created [default: ./]

Example::

    python -m cyclone.app -p foobar
    cd foobar
    twistd -n foobar

Check out the README.rst in the new project's directory for detailed information.
It ships with debian init scripts for single or multiple instances (one per cpu core)
to help make deployment as simple as possible.


Tips and Tricks
===============

As a clone, the API implemented in cyclone is almost the same of Tornado. Therefore you may use the `Tornado Documentation <http://www.tornadoweb.org/documentation>`_ for stuff like templates and so on.

The snippets below will show some tips and tricks regarding the few differences between the two.

Hello World
-----------

::

    #!/usr/bin/env python
    # coding: utf-8

    import cyclone.web
    import sys
    from twisted.internet import reactor
    from twisted.python import log

    class MainHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    def main():
        log.startLogging(sys.stdout)
        application = cyclone.web.Application([
            (r"/", MainHandler)
        ])

        reactor.listenTCP(8888, application, interface="127.0.0.1")
        reactor.run()

    if __name__ == "__main__":
        main()


Twisted Application and Plugin
------------------------------

The advantage of being a Twisted Application is that you don't need to care about basic daemon features like forking, creating pid files, changing application's user and group permissions, and selecting the proper reactor within the code.

Instead, the application may be run by ``twistd``, as follows::

    for testing:
    /usr/bin/twistd --nodaemon --python=foobar.tac

    for production:
    /usr/bin/twistd --pidfile=/var/run/foobar.pid \
                    --logfile=/var/log/foobar.log \
                    --uid=nobody --gid=nobody \
                    --reactor=epoll \
                    --python=foobar.tac

Following is the *Hello World* as a twisted application::

    # coding: utf-8
    # twisted application: foobar.tac

    import cyclone.web
    from twisted.application import service, internet

    class IndexHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("hello world")

    foobar = cyclone.web.Application([(r"/", IndexHandler)])

    application = service.Application("foobar")
    internet.TCPServer(8888, foobar(),
        interface="127.0.0.1").setServiceParent(application)


Authenticated and Asynchronous decorators
-----------------------------------------

Tornado provides decorator functions for asynchronous and authenticated
methods. Obviously, they're also implemented in cyclone, and yet more
powerful when combined with a famous Twisted decorator: ``defer.inlineCallbacks``.

The ``cyclone.web.authenticated`` decorator may be combined with ``defer.inlineCallbacks``,
however, there's a basic rule to use them together. Considering that the authenticated
decorator will check user credentials, and, depending on the result, it will
continue processing the request OR redirect the request to the login page,
it has to be used *before* the ``defer.inlineCallbacks`` to function properly::

    class IndexHandler(cyclone.web.RequestHandler):
        @cyclone.web.authenticated
        @defer.inlineCallbacks
        def get(self):
            result = yield self.do_download()
            self.write(result)

The ``cyclone.web.asynchronous`` decorator should be used with
asynchronous handers that don't use ``defer.inlineCallbacks``.  This
decorator will keep the request open until you explicitly call
``self.finish()`` later on, which is necessary if your handler needs
to continue writing to the request::

    class Indexhandler(cyclone.web.RequestHandler):
        @cyclone.web.asynchronous
        def get(self):
            download_deferred = self.do_download()
            download_deferred.addCallback(self.process_download)
            return d

        def process_download(self, result):
            self.finish(result)

If you're looking for the Cyclone equivalent of the ``tornado.gen.engine``
decorator, this is Tornado's version of ``defer.inlineCallbacks``.

Localization
------------

The ``cyclone.locale`` provides an API based on the Python ``gettext`` module.

Because of that, there is *one* extra option that may be passed to ``cyclone.locale.load_gettext_translations(path, domain="cyclone")``, which the is the gettext's domain. The default domain is *cyclone*.

Following is a step-by-step guide to implement localization in any cyclone application:

1. Create a python script or twisted application with translatable strings::

    # coding: utf-8
    # twisted application: foobar.tac

    import cyclone.web
    import cyclone.locale
    from twisted.application import service, internet

    class BaseHandler(cyclone.web.RequestHandler):
        def get_user_locale(self):
            lang = self.get_cookie("lang")
            return cyclone.locale.get(lang)

    class IndexHandler(BaseHandler):
        def get(self):
            self.render("index.html")

        def post(self):
            _ = self.locale.translate
            name = self.get_argument("name")
            self.write(_("the name is: %s" % name))

    class LangHandler(cyclone.web.RequestHandler):
        def get(self, lang):
            if lang in cyclone.locale.get_supported_locales():
                self.set_cookie("lang", lang)
            self.redirect("/")

    class Application(cyclone.web.Application):
        def __init__(self):
            handlers = [
                (r"/", IndexHandler),
                (r"/lang/(.+)", LangHandler),
            ]

            settings = {
                "static_path": "./static",
                "template_path": "./template",
            }

            cyclone.locale.load_gettext_translations("./locale", "foobar")
            cyclone.web.Application.__init__(self, handlers, **settings)

    application = service.Application("foobar")
    internet.TCPServer(8888, Application(),
        interface="127.0.0.1").setServiceParent(application)

2. Create a file in ``./template/index.html`` with translatable strings::

    <html>
    <body>
        <form action="/" method="post">
        <p>{{ _("write someone's name:") }}</p>
        <input type="text" name="name">
        <input type="submit" value="{{ _('send') }}">
        </form>

        <br>
        <p>{{ _("change language:") }}</p>
        <p><a href="/lang/en_US">English (US)</a></p>
        <p><a href="/lang/pt_BR">Portuguese (BR)</a></p>
    </body>
    </html>

3. Generate PO translatable file from the source code, using ``xgettext``:

    You will notice that ``xgettext`` cannot parse HTML properly. It was
    first designed to parse C files, and now it supports many other
    languages including Python.

    In order to parse lines like ``<input type="submit" value="{{ _('send') }}">``,
    you'll need an extra script to pre-process the files.

    Here's what you can use as ``fix.py``::

        #!/usr/bin/env python
        # coding: utf-8
        # fix.py

        import re, sys

        if __name__ == "__main__":
            try:
                filename = sys.argv[1]
                assert filename != "-"
                fd = open(filename)
            except:
                fd = sys.stdin

            line_re = re.compile(r"""['"]{{|}}['"] """)
            for line in fd:
                line = line_re.sub(r"", line)
                sys.stdout.write(line)
            fd.close()

    Then, call ``xgettext`` to generate the PO translatable file::

        cat foobar.tac template/index.html | python fix.py | \
            xgettext --language=Python --from-code=utf-8 --keyword=_:1,2 -d foobar

    This will create a file named ``foobar.po``, which needs to be
    translated, then compiled into an MO file::

        vi foobar.po
        (translate everything, :wq)

        mkdir -p ./locale/pt_BR/LC_MESSAGES/
        msgfmt foobar.po -o ./locale/pt_BR/LC_MESSAGES/foobar.mo

4. Finally, test the internationalized application::

    twistd -ny foobar.tac

There is also a complete example with pluralization in `demos/locale <http://github.com/fiorix/cyclone/tree/master/demos/locale>`_.

More options and tricks
-----------------------

- Keep-Alive

    Because of the HTTP 1.1 support, sockets aren't always closed when you call
    ``self.finish()`` in a RequestHandler. cyclone lets you enforce that by setting
    the ``no_keep_alive`` attribute attribute in some of your RequestHandlers::

        class IndexHandler(cyclone.web.RequestHandler):
            no_keep_alive = True
            def get(self):
                ...

- Socket closed notification

    One of the great features of TwistedWeb is the ``request.notifyFinish()``,
    which is also available in cyclone.
    This method returns a deferred which is fired when the request socket
    is closed, by either ``self.finish()``, someone closing their browser
    while receiving data, or closing the connection of a Comet request::

        class IndexHandler(cyclone.web.RequestHandler):
            def get(self):
                ...
                d = self.notifyFinish()
                d.addCallback(remove_from_comet_handlers_list)

- HTTP X-Headers

    When running a cyclone-based application behind `Nginx <http://nginx.org/en/>`_,
    it's very important to make it automatically use X-Real-Ip and X-Scheme HTTP
    headers. In order to make cyclone recognize those headers, the option ``xheaders=True``
    must be set in the Application settings::

        class Application(cyclone.web.Application):
            def __init__(self):
                handlers = [
                    (r"/", IndexHandler),
                ]

                settings = {
                    "xheaders": True
                    "static_path": "./static",
                }

                cyclone.web.Application.__init__(self, handlers, **settings)

- Cookie-Secret generation

    What I use to generate the "cookie_secrect" key used in cyclone.web.Application's
    settings is something pretty simple, like this::

        >>> import uuid, base64
        >>> base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        'FoQv5hgLTYCb9aKiBagpJJYtLJInWUcXilg3/vPkUnI='


FAQ
---

- Where are the request headers?

    They are part of the request, dude::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                # self.request.headers is a dict
                user_agent = self.request.headers.get("User-Agent")

- How do I access raw POST data?

    Both raw POST data and GET/DELETE un-parsed query string are available::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                raw = self.request.query

            def post(self):
                raw = self.request.body

- Where is the request information, like remote IP address, HTTP method, URI and version?

    Everything is available as request attributes::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                remote_ip = self.request.remote_ip
                method = self.request.method
                uri = self.request.uri
                version = self.request.version

- How do I set my own headers for the reply?

    Guess what, use self.set_header(name, value)::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                self.set_header("Content-Type", "application/json")
                self.finish(cyclone.escape.json_encode({"success":True}))

- What HTTP methods are supported in RequestHandler?

    Well, almost all of them. HEAD, GET, POST, DELETE, PUT and OPTIONS are supported.
    TRACE is disabled by default, because it may get you in trouble. CONNECT has nothing
    to do with web servers, it's for proxies.

    For more information on HTTP 1.1 methods, please refer to the `RFC 2612 Fielding, et al. <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_.
    For information regarding TRACE vulnerabilities, please check the following links:
    `What is HTTP TRACE? <http://www.cgisecurity.com/questions/httptrace.shtml>`_ and
    `Apache Week, security issues <http://www.apacheweek.com/issues/03-01-24#news>`_.

    Supporting different HTTP methods in the same RequestHandler is easy::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                pass

            def head(self):
                pass

            ...


Credits
=======
Thanks to (in no particular order):

- Nuswit Telephony API

  - Granting permission for this code to be published and sponsoring

- Gleicon Moraes

  - Testing and using it in the `RestMQ <http://github.com/gleicon/restmq>`_ web service

- Vanderson Mota

  - Patching setup.py and PyPi maintenance

- Andrew Badr

  - Fixing auth bugs and adding current Tornado's features

- Jon Oberheide

  - Syncing code with Tornado and security features/fixes

- `Silas Sewell <https://github.com/silas>`_

  - Syncing code and minor mail fix

- `Twitter Bootstrap <https://github.com/twitter/bootstrap>`_

  - For making our demo applications look good

- `Dan Griffin <https://github.com/dgriff1>`_

  - WebSocket Keep-Alive for OpDemand

- `Toby Padilla <https://github.com/tobypadilla>`_

  - WebSocket server
