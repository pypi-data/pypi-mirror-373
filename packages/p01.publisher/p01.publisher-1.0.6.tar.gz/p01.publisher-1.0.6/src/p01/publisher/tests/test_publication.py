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
"""IPublication Test
"""

from __future__ import absolute_import
from builtins import object
import sys
import unittest
from io import BytesIO

from zope.interface.verify import verifyObject

import p01.publisher.tests.publication
import p01.publisher.request
from p01.publisher import interfaces


class BaseIPublicationTest(object):

    # This test isn't as interesting as we'd like it to be because we
    # know too little about the semantics if a particular publication
    # object.

    def testVerifyIPublication(self):
        verifyObject(interfaces.IPublication, self._Test__new())

    def setUp(self):
        self._request = request = self._Test__request()
        self._publication = request.publication

    def testgetApplication(self):
        self._publication.getApplication(self._request)


class PublicationTest(BaseIPublicationTest, unittest.TestCase):

    def _Test__new(self):
        return p01.publisher.tests.publication.DummyPublication()

    def _Test__request(self):
        request = p01.publisher.request.BaseRequest(BytesIO(b''), {})
        request.setTraversalStack(['Engineering', 'ZopeCorp'])
        publication = self._Test__new()
        request.setPublication(publication)

        return request

    # The following are specific to our particular stub, but might be
    # good examples of tests for other implementations.

    def test_afterCall(self):
        self._publication.afterCall(self._request, None)
        self.assertEqual(self._publication._afterCall, 1)

    def test_traverseName(self):
        ob = self._publication.getApplication(self._request)
        ob = self._publication.traverseName(self._request, ob, 'ZopeCorp')
        self.assertEqual(ob.name, 'ZopeCorp')
        ob = self._publication.traverseName(self._request, ob, 'Engineering')
        self.assertEqual(ob.name, 'Engineering')

    def test_afterTraversal(self):
        self._publication.afterTraversal(self._request, None)
        self.assertEqual(self._publication._afterTraversal, 1)

    def test_beforeTraversal(self):
        self._publication.beforeTraversal(self._request)
        self.assertEqual(self._publication._beforeTraversal, 1)

    def test_callObject(self):
        result = self._publication.callObject(
            self._request, lambda request: 42)
        self.assertEqual(result, 42)

    def test_getApplication(self):
        app = p01.publisher.tests.publication.app
        result = self._publication.getApplication(self._request)
        self.assertEqual(id(result), id(app))

    def test_handleException(self):
        try:
            raise ValueError(1)
        except:
            exc_info = sys.exc_info()

        try:
            self._publication.handleException(object, self._request, exc_info)
        finally:
            exc_info = 0

    def test_callTraversalHooks(self):
        self._publication.callTraversalHooks(self._request, None)
        self.assertEqual(self._publication._callTraversalHooks, 1)

def test_suite():
    return unittest.makeSuite(PublicationTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
