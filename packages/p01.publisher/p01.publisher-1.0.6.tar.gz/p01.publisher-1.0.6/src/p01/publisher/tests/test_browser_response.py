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
"""Browser response tests
"""

from __future__ import absolute_import
import sys
import unittest

from zope.interface.verify import verifyObject

import p01.publisher.response
from p01.publisher import interfaces


class TestBrowserResponse(unittest.TestCase):

    def test_contentType_DWIM_in_setResult(self):
        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """<html>
            <blah>
            </html>
            """)
        self.assertTrue(response.getHeader('content-type').startswith("text/html")
                     )

        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """<html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(response.getHeader('content-type').startswith("text/html")
                     )

        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """<html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(response.getHeader('content-type').startswith("text/html")
                     )

        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """<!doctype html>
            <html foo="1"
            bar="x">
            <blah>
            </html>
            """)
        self.assertTrue(response.getHeader('content-type').startswith("text/html")
                     )

        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """Hello world
            """)
        self.assertTrue(response.getHeader('content-type').startswith(
            "text/plain")
                     )

        response = p01.publisher.response.BrowserResponse()
        response.setResult(
            """<p>Hello world
            """)
        self.assertTrue(
            response.getHeader('content-type').startswith("text/plain")
            )

    def test_not_DWIM_for_304_response(self):
        # Don't guess the content type with 304 responses which MUST NOT /
        # SHOULD NOT include it.
        # 
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.5
        #
        # NOTE: The content type is sill guessed if status us set after
        #       the result :(
        response = p01.publisher.response.BrowserResponse()
        response.setStatus(304)
        response.setResult(b'')
        self.assertEqual(response.getHeader('content-type'), None)

    def testInsertBase(self):
        response = p01.publisher.response.BrowserResponse()
        response.setHeader('content-type', 'text/html')

        insertBase = response._BrowserResponse__insertBase

        # Make sure that bases are inserted
        response.setBase('http://localhost/folder/')
        self.assertTrue(
            b'<base href="http://localhost/folder/" />' in
            insertBase(b'<html><head></head><body>Page</body></html>'))

        # Ensure that unicode bases work as well
        response.setBase(u'http://localhost/folder/')
        body = insertBase(b'<html><head></head><body>Page</body></html>')
        self.assertTrue(isinstance(body, bytes))
        self.assertTrue(b'<base href="http://localhost/folder/" />' in body)

        # Ensure that encoded bodies work, when a base is inserted.
        response.setBase('http://localhost/folder')
        result = insertBase(
            b'<html><head></head><body>\xc3\x9bung</body></html>')
        self.assertTrue(isinstance(body, bytes))
        self.assertTrue(b'<base href="http://localhost/folder" />' in result)

    def testInsertBaseInSetResultUpdatesContentLength(self):
        # Make sure that the Content-Length header is updated to account
        # for an inserted <base> tag.
        response = p01.publisher.response.BrowserResponse()
        response.setHeader('content-type', 'text/html')
        base = 'http://localhost/folder/'
        response.setBase(base)
        inserted_text = '\n<base href="%s" />\n' % base
        html_page = b"""<html>
            <head></head>
            <blah>
            </html>
            """
        response.setResult(html_page)
        self.assertEqual(
            int(response.getHeader('content-length')),
            len(html_page) + len(inserted_text))

    def test_interface(self):
        rp = p01.publisher.response.BrowserResponse()
        verifyObject(interfaces.IResponse, rp)
        verifyObject(interfaces.IHTTPResponse, rp)
        verifyObject(interfaces.IBrowserResponse, rp)

    def test_handleException(self):
        response = p01.publisher.response.BrowserResponse()
        try:
            raise ValueError(1)
        except:
            exc_info = sys.exc_info()

        response.handleException(exc_info)
        self.assertEqual(response.getHeader("content-type"),
            "text/html;charset=utf-8")
        self.assertEqual(response.getStatus(), 500)
        self.assertTrue(response.consumeBody() in
            [b"<html><head><title>&lt;type 'exceptions.ValueError'&gt;</title></head>\n"
             b"<body><h2>&lt;type 'exceptions.ValueError'&gt;</h2>\n"
             b"A server error occurred.\n"
             b"</body></html>\n",
             b"<html><head><title>ValueError</title></head>\n"
             b"<body><h2>ValueError</h2>\n"
             b"A server error occurred.\n"
             b"</body></html>\n"]
                     )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestBrowserResponse),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
