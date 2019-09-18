#!/usr/bin/env python
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

import re
import sys
import platform
import setuptools
from distutils import log

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Internet',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content']


setuptools.setup(
    name="cyclone",
    version="1.3",
    author="fiorix",
    author_email="fiorix@gmail.com",
    url="http://cyclone.io/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Non-blocking web server for Python. "
                "Tornado API as a Twisted protocol.",
    keywords="python non-blocking web server twisted facebook tornado",
    packages=["cyclone", "twisted.plugins", "cyclone.tests", "cyclone.testing"],
    package_data={"twisted": ["plugins/cyclone_plugin.py"],
                  "cyclone": ["appskel_default.zip",
                              "appskel_foreman.zip",
                              "appskel_signup.zip"]},
    scripts=["scripts/cyclone"],
    install_requires=["twisted==19.2.1","pyOpenSSL==19.0.0"],
    classifiers=CLASSIFIERS,
)
