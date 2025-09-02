##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
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
"""Testse

$Id: test_docs.py 5167 2025-03-06 00:11:40Z felipe.souza $
"""
from __future__ import absolute_import
__docformat__ = 'restructuredtext'

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
