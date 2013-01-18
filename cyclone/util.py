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

import zlib
from twisted.python import log


def _emit(self, eventDict):
    text = log.textFromEventDict(eventDict)
    if not text:
        return

    #print "hello? '%s'" % repr(text)
    timeStr = self.formatTime(eventDict['time'])
    #fmtDict = {'system': eventDict['system'],
    #            'text': text.replace("\n", "\n\t")}
    #msgStr = log._safeFormat("[%(system)s] %(text)s\n", fmtDict)

    log.util.untilConcludes(self.write, "%s %s\n" % (timeStr,
                                            text.replace("\n", "\n\t")))
    log.util.untilConcludes(self.flush)  # Hoorj!


log.FileLogObserver.emit = _emit


class ObjectDict(dict):
    """Makes a dictionary behave like an object."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class GzipDecompressor(object):
    """Streaming gzip decompressor.

    The interface is like that of `zlib.decompressobj` (without the
    optional arguments, but it understands gzip headers and checksums.
    """
    def __init__(self):
        # Magic parameter makes zlib module understand gzip header
        # http://stackoverflow.com/questions/1838699/\
        #    how-can-i-decompress-a-gzip-stream-with-zlib
        # This works on cpython and pypy, but not jython.
        self.decompressobj = zlib.decompressobj(16 + zlib.MAX_WBITS)

    def decompress(self, value):
        """Decompress a chunk, returning newly-available data.

        Some data may be buffered for later processing; `flush` must
        be called when there is no more input data to ensure that
        all data was processed.
        """
        return self.decompressobj.decompress(value)

    def flush(self):
        """Return any remaining buffered data not yet returned by decompress.

        Also checks for errors such as truncated input.
        No other methods may be called on this object after `flush`.
        """
        return self.decompressobj.flush()


def import_object(name):
    """Imports an object by name.

    import_object('x.y.z') is equivalent to 'from x.y import z'.

    >>> import cyclone.escape
    >>> import_object('cyclone.escape') is cyclone.escape
    True
    >>> import_object('cyclone.escape.utf8') is cyclone.escape.utf8
    True
    """
    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1])


# Fake byte literal support:  In python 2.6+, you can say b"foo" to get
# a byte literal (str in 2.x, bytes in 3.x).  There's no way to do this
# in a way that supports 2.5, though, so we need a function wrapper
# to convert our string literals.  b() should only be applied to literal
# latin1 strings.  Once we drop support for 2.5, we can remove this function
# and just use byte literals.
def b(s):
    return s


def u(s):
    return s.decode('unicode_escape')


bytes_type = str
unicode_type = unicode
basestring_type = basestring


def raise_exc_info(exc_info):
    raise exc_info[0], exc_info[1], exc_info[2]


def exec_in(code, glob, loc=None):
    exec code in glob, loc


class Configurable(object):
    """Base class for configurable interfaces.

    A configurable interface is an (abstract) class whose constructor
    acts as a factory function for one of its implementation subclasses.
    The implementation subclass as well as optional keyword arguments to
    its initializer can be set globally at runtime with `configure`.

    By using the constructor as the factory method, the interface looks like
    a normal class, ``isinstance()`` works as usual, etc.  This pattern
    is most useful when the choice of implementation is likely to be a
    global decision (e.g. when epoll is available, always use it instead of
    select), or when a previously-monolithic class has been split into
    specialized subclasses.

    Configurable subclasses must define the class methods
    `configurable_base` and `configurable_default`, and use the instance
    method `initialize` instead of `__init__`.
    """
    __impl_class = None
    __impl_kwargs = None

    def __new__(cls, **kwargs):
        base = cls.configurable_base()
        args = {}
        if cls is base:
            impl = cls.configured_class()
            if base.__impl_kwargs:
                args.update(base.__impl_kwargs)
        else:
            impl = cls
        args.update(kwargs)
        instance = super(Configurable, cls).__new__(impl)
        # initialize vs __init__ chosen for compatiblity with AsyncHTTPClient
        # singleton magic.  If we get rid of that we can switch to __init__
        # here too.
        instance.initialize(**args)
        return instance

    @classmethod
    def configurable_base(cls):
        """Returns the base class of a configurable hierarchy.

        This will normally return the class in which it is defined.
        (which is *not* necessarily the same as the cls classmethod parameter).
        """
        raise NotImplementedError()

    @classmethod
    def configurable_default(cls):
        """Returns the implementation class to be used if none is
        configured."""
        raise NotImplementedError()

    def initialize(self):
        """Initialize a `Configurable` subclass instance.

        Configurable classes should use `initialize` instead of `__init__`.
        """

    @classmethod
    def configure(cls, impl, **kwargs):
        """Sets the class to use when the base class is instantiated.

        Keyword arguments will be saved and added to the arguments passed
        to the constructor.  This can be used to set global defaults for
        some parameters.
        """
        base = cls.configurable_base()
        if isinstance(impl, (unicode_type, bytes_type)):
            impl = import_object(impl)
        if impl is not None and not issubclass(impl, cls):
            raise ValueError("Invalid subclass of %s" % cls)
        base.__impl_class = impl
        base.__impl_kwargs = kwargs

    @classmethod
    def configured_class(cls):
        """Returns the currently configured class."""
        base = cls.configurable_base()
        if cls.__impl_class is None:
            base.__impl_class = cls.configurable_default()
        return base.__impl_class

    @classmethod
    def _save_configuration(cls):
        base = cls.configurable_base()
        return (base.__impl_class, base.__impl_kwargs)

    @classmethod
    def _restore_configuration(cls, saved):
        base = cls.configurable_base()
        base.__impl_class = saved[0]
        base.__impl_kwargs = saved[1]


def doctests():
    import doctest
    return doctest.DocTestSuite()
