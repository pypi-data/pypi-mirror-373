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
"""baserequest tests
"""

from __future__ import absolute_import
import unittest
from io import BytesIO

from p01.publisher.tests.publication import DummyPublication
from p01.publisher.tests.basetestipublicationrequest \
     import BaseTestIPublicationRequest
from p01.publisher.tests.basetestipublisherrequest \
     import BaseTestIPublisherRequest
from p01.publisher.tests.basetestiapplicationrequest \
     import BaseTestIApplicationRequest

import p01.publisher.request


class TestBaseRequest(BaseTestIPublicationRequest,
                      BaseTestIApplicationRequest,
                      BaseTestIPublisherRequest,
                      unittest.TestCase):

    def _Test__new(self, **kw):
        return p01.publisher.request.BaseRequest(BytesIO(), kw)

    def _Test__expectedViewType(self):
        return None # we don't expect

    def test_IApplicationRequest_bodyStream(self):
        request = p01.publisher.request.BaseRequest(BytesIO(b'spam'), {})
        self.assertEqual(request.bodyStream.read(), b'spam')

    def test_IPublicationRequest_getPositionalArguments(self):
        self.assertEqual(self._Test__new().getPositionalArguments(), ())

    def test_IPublisherRequest_traverse(self):
        request = self._Test__new()
        request.setPublication(DummyPublication())
        app = request.publication.getApplication(request)

        request.setTraversalStack([])
        self.assertEqual(request.traverse(app).name, '')
        self.assertEqual(request._last_obj_traversed, app)
        request.setTraversalStack(['ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'ZopeCorp')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp)
        request.setTraversalStack(['Engineering', 'ZopeCorp'])
        self.assertEqual(request.traverse(app).name, 'Engineering')
        self.assertEqual(request._last_obj_traversed, app.ZopeCorp.Engineering)

    def test_IPublisherRequest_processInputs(self):
        self._Test__new().processInputs()

    def test_AnnotationsExist(self):
        self.assertEqual(self._Test__new().annotations, {})

    # Needed by BaseTestIEnumerableMapping tests:
    def _IEnumerableMapping__stateDict(self):
        return {'id': 'ZopeOrg', 'title': 'Zope Community Web Site',
                'greet': 'Welcome to the Zope Community Web site'}

    def _IEnumerableMapping__sample(self):
        return self._Test__new(**(self._IEnumerableMapping__stateDict()))

    def _IEnumerableMapping__absentKeys(self):
        return 'foo', 'bar'

    def test_SetRequestInResponse(self):
        request = self._Test__new()
        self.assertEqual(request.response._request, request)


def test_suite():
    return unittest.makeSuite(TestBaseRequest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
