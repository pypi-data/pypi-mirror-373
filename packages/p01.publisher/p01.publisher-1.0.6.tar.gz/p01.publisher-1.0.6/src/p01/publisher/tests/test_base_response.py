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
"""Tests for BaseResponse
"""

from __future__ import absolute_import
import unittest

from zope.interface.verify import verifyObject

import p01.publisher.response
from p01.publisher import interfaces


class TestBaseResponse(unittest.TestCase):

    def test_interface(self):
        verifyObject(interfaces.IResponse, p01.publisher.response.BaseResponse())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestBaseResponse),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
