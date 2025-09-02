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
"""IPublisherReuqest Test
"""

from __future__ import absolute_import
from builtins import object
from zope.interface.verify import verifyObject
from zope.publisher.interfaces import IPublisherRequest

from p01.publisher.tests.publication import DummyPublication


class BaseTestIPublisherRequest(object):

    def testVerifyIPublisherRequest(self):
        verifyObject(IPublisherRequest, self._Test__new())

    def testHaveCustomTestsForIPublisherRequest(self):
        # Make sure that tests are defined for things we can't test here
        self.test_IPublisherRequest_traverse
        self.test_IPublisherRequest_processInputs

    def testPublicationManagement(self):
        request = self._Test__new()
        publication = DummyPublication()
        request.setPublication(publication)
        self.assertEqual(id(request.publication), id(publication))
