=======
cyclone
=======
:Info: See `github <https://github.com/fiorix/cyclone>`_ for the latest source.
:Author: Alexandre Fiori <fiorix@gmail.com>


About
=====

cyclone is a clone of facebook's `Tornado <http://tornadoweb.org>`_, on top of
`Twisted <http://twistedmatrix.com>`_.

Although cyclone and tornado are very similar, cyclone leverages all
enterprise class features of Twisted, and more. It is extremely stable, and
ready for production.


Features
--------

**cyclone is a Twisted protocol**. Thus, it may be used in conjunction with
any other protocol implemented in Twisted. The same server can deliver HTTP
content on one port, SSH on another, and it can keep a pool of persistent,
non-blocking connections to several databases. All in a single process.

Web apps built with cyclone are **fully translatable**. The localization system
is based on `Gettext <http://www.gnu.org/software/gettext/>`_. It's possible
to translate strings in the server code, as well as text and HTML templates.

**Secure**. It can deliver HTTP and **HTTPS (SSL)** on the same server, with
individual request routing mechanism. Also, cyclone supports the standard HTTP
Authentication, which can be used to implement HTTP Basic, Digest, or any
other hand crafted authentication system, like `Amazon's S3
<http://docs.amazonwebservices.com/AmazonS3/latest/dev/RESTAuthentication.html>`_.

**API friendly**. cyclone is very useful for writing web services, RESTful or
any other type of web API. Features like HTTP Keep-Alive and XSRF can be
enabled or disabled per request, which means the server can have different
behaviour when communicating with browsers, or other custom HTTP clients.

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

Check out the `benchmarks <http://wiki.github.com/fiorix/cyclone/benchmarks>`_
page.


Installing
----------

cyclone can be installed from ``pip`` or ``easy_install``::

    $ pip install cyclone

It has no external dependencies other than Twisted 10 or newer, running
on Python 2.6 or 2.7, or PyPy 1.8 or 1.9.

It runs on Python 2.5 too, but requires the ``simplejson`` module. Also, it
runs on PyPy 1.8 as long as there's no SSL.

On most Linux distributions, such as Debian, twisted is splitted in several
packages. In this case, you'll need at least ``python-twisted-core``,
``python-twisted-web``, and optionally ``python-twisted-mail`` - if you want to
be able to send e-mails straight from cyclone apps.

Source code is available on `https://github.com/fiorix/cyclone
<https://github.com/fiorix/cyclone>`_, and ships with very useful and
comprehensive demo applications.

Check out the `demos <https://github.com/fiorix/cyclone/tree/master/demos>`_.


Running, and deploying
----------------------

cyclone apps can be run by ``twistd``, and it's the easiest way to start
playing with the framework.

This is ``hello.py``::

    import cyclone.web


    class MainHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("hello, world")


    Application = lambda: cyclone.web.Application([(r"/", MainHandler)])

A dev server can be started like this::

    $ twistd -n cyclone -r hello.Application
    Log opened.
    reactor class: twisted.internet.selectreactor.SelectReactor.
    cyclone.web.Application starting on 8888

Due to the power of ``twistd``, cyclone apps can be easily deployed in
production, with all the basic features of standard daemons::

    $ twistd --uid=www-data --gid=www-data --reactor=epoll \
             --logfile=/var/log/hello.log --pidfile=/var/run/hello.log \
             cyclone --port=80 --listen=0.0.0.0 --app=hello.Application

Process permissions are properly set, log files rotate automatically,
syslog is also an option, pid files are generated so other subsystems can
use it on start/stop scripts.

Setting up SSL on the same server is just a matter or creating a certificate
and adding ``--ssl-app=hello.Application`` to the command line. It could easily
point to yet another ``Application`` class, with a completely different URL
routing. Check out the `SSL demo
<https://github.com/fiorix/cyclone/tree/master/demos/ssl>`_.

Run ``twistd --help`` for more details. Here's a complete list of options
supported by the cyclone twisted plugin::

    $ twistd cyclone --help
    Usage: twistd [options] cyclone [options]
    Options:
      -p, --port=         tcp port to listen on [default: 8888]
      -l, --listen=       interface to listen on [default: 127.0.0.1]
      -r, --app=          cyclone application to run
      -c, --appopts=      arguments to your application
          --ssl-port=     port to listen on for ssl [default: 8443]
          --ssl-listen=   interface to listen on for ssl [default: 127.0.0.1]
          --ssl-cert=     ssl certificate [default: server.crt]
          --ssl-key=      ssl server key [default: server.key]
          --ssl-app=      ssl application (same as --app)
          --ssl-appopts=  arguments to the ssl application
          --version
          --help          Display this help and exit.


Project template
----------------

cyclone ships with a full featured project template. It helps on avoiding the
repetitive process of creating a basic project structure, like parsing
configuration files, setting up database connections, and translation of code
and HTML templates.

::

    $ python -m cyclone.app --help

    use: cyclone.app [options]
    Options:
     -h --help              Show this help.
     -p --project=NAME      Create new cyclone project.
     -g --git               Use in conjunction with -p to make it a git repository.
     -m --modname=NAME      Use another name for the module [default: project_name]
     -v --version=VERSION   Set project version [default: 0.1]
     -s --set-pkg-version   Set version on package name [default: False]
     -t --target=PATH       Set path where project is created [default: ./]
     -l --license=FILE      Append the following license file [default: Apache 2]
     -f --foreman           Create a foreman based project (suited to run on heroku and other PaaS)

Creating new projects can be as simple as running this::

    $ python -m cyclone.app -p foobar

Check README.rst in the new project directory for detailed information on how
to use it.

The template ships with Debian init scripts for running ``twistd`` as single,
or multiple instances (one per CPU core) to help make deployments as simple as
possible.

If you are into PaaS (heroku for example) or just using foreman to manage your applications, create your application like this ::
    
    $ python -m cyclone.app -f -p foobar

and check the README.rst for further instructions.


Tips and Tricks
===============

As a clone, the API implemented in cyclone is almost the same of Tornado.
Therefore you may use `Tornado Documentation
<http://www.tornadoweb.org/documentation>`_ for things like auth, and the
template engine.

The snippets below will show some tips and tricks regarding the few differences
between the two.


Deferreds
---------

First things first: you don't need to care about deferreds at all to start
playing with cyclone. `http://cyclone.io/ssedemo <http://cyclone.io/ssedemo>`_
is an example.

However, `Deferreds
<http://twistedmatrix.com/documents/current/core/howto/defer.html>`_ might
help take your app to a whole new level.

cyclone uses deferreds extensively, to provide persistent database connections,
and, generally speaking, to allow web apps to easily communicate with other
subsystems on demand, while handling HTTP requests.

Here's an example, ``crawler.py``::

    # run: twistd -n cyclone -r crawler.Application

    import cyclone.web
    from twisted.internet import defer
    from twisted.web.client import getPage


    class MainHandler(cyclone.web.RequestHandler):
        @defer.inlineCallbacks
        def get(self):
            response = yield getPage("http://freegeoip.net/xml/")
            self.set_header("Content-Type", "text/plain")
            self.write(response)


    Application = lambda: cyclone.web.Application([("/", MainHandler)], debug=True)

The example above is an app that makes a new request to ``freegeoip.net`` on
each request it takes, and respond to this request with whatever it gets from
freegeoip. All without blocking the server.

The exact same concept is used to communicate with databases. Basically, using
``inlineCallbacks`` eliminates the nightmare of dealing with chained deferreds
and their responses in different callbacks. This way is simple and
straightforward.

Here is another example, ``delayed.py``::

    # run: twistd -n cyclone -r delayed.Application

    import cyclone.web
    from twisted.internet import defer
    from twisted.internet import reactor


    def sleep(n):
        d = defer.Deferred()
        reactor.callLater(n, lambda: d.callback(None))
        return d


    class MainHandler(cyclone.web.RequestHandler):
        @defer.inlineCallbacks
        def get(self):
            yield sleep(5)
            self.write("hello, world")


    Application = lambda: cyclone.web.Application([("/", MainHandler)], debug=True)

There are other useful examples in the `demos
<https://github.com/fiorix/cyclone/tree/master/demos/ssl>`_ directory. Take a
look at ``demos/email``, ``demos/redis``, and ``demos/httpauth``.


The @asynchronous decorator
---------------------------

By default, cyclone will terminate the request after it is processed by the
``RequestHandler``. Consider this code::

    class MainHandler(cyclone.web.RequestHandler):
        def get(self):
            self.write("hello, world")

The above request is always terminated after ``get`` returns. Even if ``get``
returns a deferred, the request is automatically terminated after the deferred
is fired.

The ``cyclone.web.asynchronous`` decorator can be used to keep the request
open until ``self.finish()`` is explicitly called. The request will be in a
stale state, allowing for sending late, and incremental (chunked) responses.

Here's an example, ``clock.py``::

    # run: twistd -n cyclone -r clock.Application

    import cyclone.web
    import time
    from twisted.internet import task
    from twisted.internet import reactor


    class MessagesMixin(object):
        clients = []

        @classmethod
        def setup(self):
            task.LoopingCall(MessagesMixin.broadcast).start(1)

        @classmethod
        def broadcast(self):
            for req in MessagesMixin.clients:
                req.write("%s\r\n" % time.ctime())
                req.flush()


    class MainHandler(cyclone.web.RequestHandler, MessagesMixin):
        @cyclone.web.asynchronous
        def get(self):
            self.set_header("Content-Type", "text/plain")
            self.clients.append(self)
            d = self.notifyFinish()
            d.addCallback(lambda *ign: self.clients.remove(self))


    class Application(cyclone.web.Application):
        def __init__(self):
            reactor.callWhenRunning(MessagesMixin.setup)
            cyclone.web.Application.__init__(self, [("/", MainHandler)])

This server will never terminate client connections. Instead, it'll send one
message per second, to all clients, forever.

Whenever the client disconnects, it's automatically removed from the list of
connected clients - ``notifyFinish()`` returns a deferred, which is fired
when the connection is terminated.


Mixing @inlineCallbacks, @asynchronous and @authenticated
---------------------------------------------------------

A quick refresh: ``@inlineCallbacks`` turns decorated functions into
deferreds so they can cooperatively call functions that returns deferreds
and handle their results inline, making the code much simpler.
``@asynchronous`` is used to keep the connection open until explicitly
terminated. And ``@authenticated`` is used to require the client to be logged
in, usually via a control Cookie.

All can be mixed up, but some care has to be taken.

When multiple decorators are applied to a request method, ``@authenticated``
must always be the first (top of other decorators). The reason for this, is
because if authentication fails the request shouln't be processed.

For the other two, ``inlineCallbacks`` and ``@authenticated``, sequence doesn't
really matter.

::

    class MainHandler(cyclone.web.RequestHandler):
        @cyclone.web.authenticated
        @cyclone.web.asynchronous
        @defer.inlineCallbacks
        def get(self):
            ...

        @cyclone.web.authenticated
        @defer.inlineCallbacks
        @cyclone.web.asynchronous
        def post(self):
            ...


Localization
------------

``cyclone.locale`` uses ``gettext`` to provide translation to strings in the
server code, and any other text or HTML templates.

It must be initialized with a domain, which is where all translation messages
are stored. Refer to the ``gettext`` manual for details on usage, domains, etc.

The default domain is *cyclone*, and must be changed to the name of your app
or module. All translation files are named after the domain.

There is a complete example of internationalized web application in
`demos/locale <https://github.com/fiorix/cyclone/tree/master/demos/locale>`_.

Also, the project template that ships with cyclone is already prepared for
full translation. Give it a try::

    $ python -m cyclone.app -p foobar

Then check the contents of ``foobar/``.


Other important things
----------------------

- Keep-Alive

    Because of the HTTP 1.1 support, sockets aren't always closed when you call
    ``self.finish()`` in a ``RequestHandler``. cyclone lets you enforce that by
    setting the ``no_keep_alive`` class attribute attribute::

        class IndexHandler(cyclone.web.RequestHandler):
            no_keep_alive = True
            def get(self):
                ...

    With this, cyclone will always close the socket after ``self.finish()`` is
    called on all methods (get, post, etc) of this ``RequestHandler`` class.

- XSRF

    By default, XSRF is either enabled or disabled for the entire server,
    because it's set in Application's settings::

        cyclone.web.Application(handlers, xsrf_cookies=True)

    That might be a problem if the application is also serving an API, like
    a RESTful API supposed to work with HTTP clients other than the browser.

    For those endpoints, it's possible to disable XSRF::

        class WebLoginHandler(cyclone.web.RequestHandler):
            def post(self):
                u = self.get_argument("username")
                ...

        class APILoginHandler(cyclone.web.RequestHandler):
            no_xsrf = True

            def post(self):
                u = self.get_argument("username")
                ...

- Socket closed notification

    One of the great features of ``TwistedWeb`` is the
    ``request.notifyFinish()``, which is also available in cyclone.

    This method returns a deferred, which is fired when the request socket
    is closed, by either ``self.finish()``, someone closing their browser
    while receiving data, or closing the connection of a Comet request::

        class IndexHandler(cyclone.web.RequestHandler):
            def get(self):
                ...
                d = self.notifyFinish()
                d.addCallback(remove_from_comet_handlers_list)

            def on_finish(self):
                # alternative to notifyFinish
                pass

    This was implemented before Tornado added support to ``on_finish``.
    Currently, both methods are supported in cyclone.

- HTTP X-Headers

    When running a cyclone-based application behind `Nginx
    <http://nginx.org/en/>`_, it's very important to make it automatically use
    X-Real-Ip and X-Scheme HTTP headers. In order to make cyclone recognize
    those headers, the option ``xheaders=True`` must be set in the Application
    settings::

        cyclone.web.Application(handlers, xheaders=True)

- Cookie-Secret generation

    The following code can be used to generate random cookie secrets::

        >>> import uuid, base64
        >>> base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        'FoQv5hgLTYCb9aKiBagpJJYtLJInWUcXilg3/vPkUnI='

- SSL

    cyclone can serve SSL or sit behind a termination proxy (e.g. Nginx).
    Make sure that you bind the right port with listenSSL, passing the certs::

        import cyclone.web
        import sys
        from twisted.internet import reactor
        from twisted.internet import ssl
        from twisted.python import log


        class MainHandler(cyclone.web.RequestHandler):
            def get(self):
                self.write("Hello, world")


        def main():
            log.startLogging(sys.stdout)
            application = cyclone.web.Application([(r"/", MainHandler)])

            interface = "127.0.0.1"
            reactor.listenTCP(8888, application, interface=interface)
            reactor.listenSSL(8443, application,
                              ssl.DefaultOpenSSLContextFactory("server.key",
                                                               "server.crt"),
                              interface=interface)
            reactor.run()


        if __name__ == "__main__":
            main()

    This example plus a script to generate certificates sits under `demos/ssl
    <https://github.com/fiorix/cyclone/tree/master/demos/ssl>`_.

FAQ
---

- Where are the request headers?

    They are part of the request, dude::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                # self.request.headers is a dict
                user_agent = self.request.headers.get("User-Agent")

- How do I access raw POST data?

    Both raw POST data and GET/DELETE un-parsed query strings are available::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                raw = self.request.query

            def post(self):
                raw = self.request.body

- Where is the request information like remote IP address, etc?

    Everything is available as request attributes, like protocol, HTTP method,
    URI and version::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                proto = self.request.protocol
                remote_ip = self.request.remote_ip
                method = self.request.method
                uri = self.request.uri
                version = self.request.version

- How do I set my own headers for the reply?

    Guess what, use ``self.set_header(name, value)``::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                self.set_header("Content-Type", "application/json")
                self.finish(cyclone.escape.json_encode({"success":True}))

- What HTTP methods are supported in RequestHandler?

    Well, almost all of them. HEAD, GET, POST, DELETE, PATCH, PUT and OPTIONS are
    supported. TRACE is disabled by default, because it may get you in trouble.
    CONNECT has nothing to do with web servers, it's for proxies.

    For more information on HTTP 1.1 methods, please refer to the `RFC 2612
    Fielding, et al. <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_.

    For information regarding TRACE vulnerabilities, please check the following
    links:
    `What is HTTP TRACE?
    <http://www.cgisecurity.com/questions/httptrace.shtml>`_ and
    `Apache Week, security issues
    <http://www.apacheweek.com/issues/03-01-24#news>`_.

    Supporting different HTTP methods in the same RequestHandler is easy::

        class MyHandler(cyclone.web.RequestHandler):
            def get(self):
                pass

            def head(self):
                pass

            def post(self):
                pass

            def delete(self):
                pass

- How to handle file uploads?

    They are available inside the request object as ``self.request.files``.
    Make sure your HTML form encoding is ``multipart/form-data``::

        class MyHandler(cyclone.web.RequestHandler):
            def post(self):
                photos = self.request.files.get("photos")

                # Because it's possible to upload several files under the
                # same form name, we fetch the first uploaded photo.
                first_photo = photos[0]

                # first_photo.filename: original filename
                # first_photo.content_type: parsed content type (not mime-type)
                # first_photo.body: file contents

    There's an example in `demos/upload
    <https://github.com/fiorix/cyclone/tree/master/demos/upload>`_.


Credits
=======
Thanks to (in no particular order):

- Nuswit Telephony API

  - Granting permission for this code to be published and sponsoring

- Gleicon Moraes

  - Testing and using it in the `RestMQ <https://github.com/gleicon/restmq>`_ web service

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

- `Jeethu Rao <https://github.com/jeethu>`_

  - Minor bugfixes and patches

- `Flavio Grossi <https://github.com/flaviogrossi>`_

  - Minor code fixes and websockets chat statistics example

- `Gautam Jeyaraman <https://github.com/gautamjeyaraman>`_

  - Minor code fixes and patches
