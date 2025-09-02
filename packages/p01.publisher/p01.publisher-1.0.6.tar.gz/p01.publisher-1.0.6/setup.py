##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: setup.py 5657 2025-09-01 13:33:32Z roger.ineichen $
"""

from __future__ import absolute_import
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.publisher',
    version='1.0.6',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "NO ZODB publisher components for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope zope3 z3c ZODB",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.publisher',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'zope.testing',
            'p01.checker',
            'p01.testbrowser',
             ]),
    install_requires = [
        'setuptools',
        'ZConfig',
        'p01.cgi',
        'p01.json',
        'p01.jsonrpc',
        'transaction',
        'zope.authentication',
        'zope.browser',
        'zope.component',
        'zope.configuration',
        'zope.error',
        'zope.event',
        'zope.processlifetime',
        'zope.i18n',
        'zope.interface>=5.5.2',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.site',
        'zope.testing',
        'zope.traversing',
        ],
    entry_points={
        'paste.app_factory': [
            'app = p01.publisher.wsgi:application_factory',
            'zodb = p01.publisher.wsgi:zodb_application_factory',
        ]
    },
    zip_safe = False,
)