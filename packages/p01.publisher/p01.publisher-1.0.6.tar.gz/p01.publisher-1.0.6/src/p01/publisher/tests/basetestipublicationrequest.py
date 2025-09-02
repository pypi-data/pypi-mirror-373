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
"""IPublicationRequest base test
"""
from __future__ import absolute_import
from builtins import object
import sys

import zope.interface
from zope.interface.verify import verifyObject
from zope.publisher.interfaces import IPublicationRequest
from zope.publisher.interfaces import IHeld
from zope.publisher.interfaces.browser import IBrowserSkinType


@zope.interface.implementer(IHeld)
class Held(object):

    released = False

    def release(self):
        self.released = True


class BaseTestIPublicationRequest(object):

    def testVerifyIPublicationRequest(self):
        verifyObject(IPublicationRequest, self._Test__new())

    def testHaveCustomTestsForIPublicationRequest(self):
        # Make sure that tests are defined for things we can't test here
        self.test_IPublicationRequest_getPositionalArguments

    def testTraversalStack(self):
        request = self._Test__new()
        stack = ['Engineering', 'ZopeCorp']
        request.setTraversalStack(stack)
        self.assertEqual(list(request.getTraversalStack()), stack)

    def testHoldCloseAndGetResponse(self):
        request = self._Test__new()

        response = request.response
        rcresponse = sys.getrefcount(response)

        resource = object()
        rcresource = sys.getrefcount(resource)

        request.hold(resource)

        resource2 = Held()
        rcresource2 = sys.getrefcount(resource2)
        request.hold(resource2)

        self.assertTrue(sys.getrefcount(resource) > rcresource)
        self.assertTrue(sys.getrefcount(resource2) > rcresource2)
        self.assertFalse(resource2.released)

        request.close()

        self.assertTrue(resource2.released)
        # Responses are not unreferenced during close()
        self.assertTrue(sys.getrefcount(response) >= rcresponse)
        self.assertEqual(sys.getrefcount(resource), rcresource)
        self.assertEqual(sys.getrefcount(resource2), rcresource2)

    def testSkinManagement(self):
        request = self._Test__new()

        class IMoreFoo(zope.interface.Interface):
            pass
        zope.interface.directlyProvides(IMoreFoo, IBrowserSkinType)

        self.assertEqual(IMoreFoo.providedBy(request), False)
        zope.interface.directlyProvides(request, IMoreFoo)
        self.assertEqual(IMoreFoo.providedBy(request), True)

