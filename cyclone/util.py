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

import sys

from twisted.python import log


def _emit(self, eventDict):
    text = log.textFromEventDict(eventDict)
    if not text:
        return

    # print "hello? '%s'" % repr(text)
    timeStr = self.formatTime(eventDict['time'])
    # fmtDict = {'system': eventDict['system'],
    #            'text': text.replace("\n", "\n\t")}
    # msgStr = log._safeFormat("[%(system)s] %(text)s\n", fmtDict)

    log.util.untilConcludes(self.write, "%s %s\n" % (timeStr,
                                                     text.replace("\n", "\n\t")))
    log.util.untilConcludes(self.flush)  # Hoorj!


# monkey patch, sorry
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
    method = getattr(obj, parts[-1], None)
    if method:
        return method
    else:
        raise ImportError("No method named %s" % parts[-1])

# Fake unicode literal support:  Python 3.2 doesn't have the u'' marker for
# literal strings, and alternative solutions like "from __future__ import
# unicode_literals" have other problems (see PEP 414).  u() can be applied
# to ascii strings that include \u escapes (but they must not contain
# literal non-ascii characters).

if not isinstance(b'', type('')):
    def u(s):
        return s
    unicode_type = str
    basestring_type = str
else:
    def u(s):
        return s.decode('unicode_escape')
    # These names don't exist in py3, so use noqa comments to disable
    # warnings in flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

bytes_type = str

if sys.version_info < (3,):
    unicode_type = unicode
    unicode_char_type = unichr
    basestring_type = basestring
    import types
    list_type = types.ListType
    dict_type = types.DictType
    int_type = types.IntType
    tuple_type = types.TupleType
    string_type = types.StringType
    string_types = types.StringTypes
    exec("""
def raise_exc_info(exc_info):
    raise exc_info[0], exc_info[1], exc_info[2]

def exec_in(code, glob, loc=None):
    if isinstance(code, basestring):
        # exec(string) inherits the caller's future imports; compile
        # the string first to prevent that.
        code = compile(code, '<string>', 'exec', dont_inherit=True)
    exec code in glob, loc
""")
else:
    unicode_type = str
    unicode_char_type = chr
    basestring_type = str
    list_type = list
    dict_type = dict
    int_type = int
    tuple_type = tuple
    string_type = str
    string_types = str
    exec("""
def raise_exc_info(exc_info):
    raise exc_info[1].with_traceback(exc_info[2])

def exec_in(code, glob, loc=None):
    if isinstance(code, str):
        code = compile(code, '<string>', 'exec', dont_inherit=True)
    exec(code, glob, loc)
""")

def doctests():  # pragma: no cover
    import doctest
    return doctest.DocTestSuite()
