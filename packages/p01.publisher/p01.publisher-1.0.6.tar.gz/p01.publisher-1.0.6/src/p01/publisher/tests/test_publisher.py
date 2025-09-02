##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Test Publisher
"""

from __future__ import absolute_import
from builtins import object
import unittest
from io import BytesIO

import zope.interface
import zope.component
from zope.interface.verify import verifyClass
from zope.publisher.interfaces import Unauthorized
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import DebugError
from zope.publisher.interfaces import IReRaiseException
from zope.publisher.interfaces import Retry

import p01.publisher.tests.publication
from p01.publisher import interfaces
from p01.publisher.publisher import publish
from p01.publisher.testing import TestRequest


class PublisherTests(unittest.TestCase):

    def setUp(self):
        class AppRoot(object):
            """Required docstring for the publisher."""

        class Folder(object):
            """Required docstring for the publisher."""

        class Item(object):
            """Required docstring for the publisher."""
            def __call__(self):
                return "item"

        class NoDocstringItem(object):
            def __call__(self):
                return "Yo! No docstring!"

        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()

        self.app._item = Item()
        self.app.noDocString = NoDocstringItem()

    def _createRequest(self, path, **kw):
        publication = p01.publisher.tests.publication.DefaultPublication(self.app)
        path = path.split('/')
        path.reverse()
        request = TestRequest(BytesIO(b''), **kw)
        request.setTraversalStack(path)
        request.setPublication(publication)
        return request

    def _publisherResults(self, path, **kw):
        request = self._createRequest(path, **kw)
        response = request.response
        publish(request, handleErrors=False)
        return response._result

    def _registerExcAdapter(self, factory):
        zope.component.provideAdapter(factory, (Unauthorized,), IReRaiseException)

    def _unregisterExcAdapter(self, factory):
        gsm = zope.component.getGlobalSiteManager()
        gsm.unregisterAdapter(
            factory=factory, required=(Unauthorized,),
            provided=IReRaiseException)

    def testImplementsIPublication(self):
        self.assertTrue(interfaces.IPublication.providedBy(
            p01.publisher.tests.publication.DefaultPublication(self.app)))

    def testInterfacesVerify(self):
        for interface in zope.interface.implementedBy(
            p01.publisher.tests.publication.DefaultPublication):
            verifyClass(interface,
            p01.publisher.tests.publication.DefaultPublication)

    def testTraversalToItem(self):
        res = self._publisherResults('/folder/item')
        self.assertEqual(res, (b'item',))
        res = self._publisherResults('/folder/item/')
        self.assertEqual(res, (b'item',))
        res = self._publisherResults('folder/item')
        self.assertEqual(res, (b'item',))

    def testUnderscoreUnauthorizedException(self):
        self.assertRaises(Unauthorized, self._publisherResults, '/_item')

    def testNotFoundException(self):
        self.assertRaises(NotFound, self._publisherResults, '/foo')

    def testDebugError(self):
        self.assertRaises(DebugError, self._publisherResults, '/noDocString')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(PublisherTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
