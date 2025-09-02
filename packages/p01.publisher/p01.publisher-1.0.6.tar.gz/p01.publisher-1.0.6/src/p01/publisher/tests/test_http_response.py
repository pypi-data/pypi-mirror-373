# -*- coding: latin-1 -*-
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
"""HTTP Publisher Tests
"""

from __future__ import absolute_import
import sys
import unittest

import zope.testing.cleanup
from zope.interface.verify import verifyObject
from zope.publisher.http import DirectResult

import p01.publisher.response

from p01.publisher import interfaces


class TestHTTPResponse(unittest.TestCase):

    def testInterface(self):
        rp = p01.publisher.response.HTTPResponse()
        verifyObject(interfaces.IResponse, rp)
        verifyObject(interfaces.IHTTPResponse, rp)

    def _createResponse(self):
        response = p01.publisher.response.HTTPResponse()
        return response

    def _parseResult(self, response):
        return dict(response.getHeaders()), response.consumeBody()

    def _getResultFromResponse(self, body, charset='utf-8', headers=None):
        response = self._createResponse()
        assert(charset == 'utf-8')
        if headers is not None:
            for hdr, val in list(headers.items()):
                response.setHeader(hdr, val)
        response.setResult(body)
        return self._parseResult(response)

    def testWrite_noContentLength(self):
        response = self._createResponse()
        # We have to set all the headers ourself, we choose not to provide a
        # content-length header
        response.setHeader('Content-Type', 'text/plain;charset=us-ascii')

        # Output the data
        data = b'a'*10
        response.setResult(DirectResult(data))

        headers, body = self._parseResult(response)
        # Check that the data have been written, and that the header
        # has been preserved
        self.assertEqual(headers['Content-Type'],
                         'text/plain;charset=us-ascii')
        self.assertEqual(body, data)

        # Make sure that no Content-Length header was added
        self.assertTrue('Content-Length' not in headers)

    def testContentLength(self):
        eq = self.assertEqual

        headers, body = self._getResultFromResponse("test", "utf-8",
            {"content-type": "text/plain"})
        eq("4", headers["Content-Length"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(
            u'\u0442\u0435\u0441\u0442', "utf-8",
            {"content-type": "text/plain"})
        eq("8", headers["Content-Length"])
        eq(b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82', body)

    def testContentType(self):
        eq = self.assertEqual

        headers, body = self._getResultFromResponse(b"test", "utf-8")
        eq("", headers.get("Content-Type", ""))
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test",
            headers={"content-type": "text/plain"})
        eq("text/plain;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "text/html"})
        eq("text/html;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "text/plain;charset=cp1251"})
        eq("text/plain;charset=cp1251", headers["Content-Type"])
        eq(b"test", body)

        # see https://bugs.launchpad.net/zope.publisher/+bug/98395
        # RFC 3023 types and */*+xml output as unicode

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "text/xml"})
        eq("text/xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "application/xml"})
        eq("application/xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "text/xml-external-parsed-entity"})
        eq("text/xml-external-parsed-entity;charset=utf-8",
           headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "application/xml-external-parsed-entity"})
        eq("application/xml-external-parsed-entity;charset=utf-8",
           headers["Content-Type"])
        eq(b"test", body)

        # Mozilla XUL
        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "application/vnd+xml"})
        eq("application/vnd+xml;charset=utf-8", headers["Content-Type"])
        eq(b"test", body)

        # end RFC 3023 / xml as unicode

        headers, body = self._getResultFromResponse(b"test", "utf-8",
            {"content-type": "image/gif"})
        eq("image/gif", headers["Content-Type"])
        eq(b"test", body)

        headers, body = self._getResultFromResponse(u"test", "utf-8",
            {"content-type": "application/json"})
        eq("application/json", headers["Content-Type"])
        eq(b"test", body)

    def _getCookieFromResponse(self, cookies):
        # Shove the cookies through request, parse the Set-Cookie header
        # and spit out a list of headers for examination
        response = self._createResponse()
        for name, value, kw in cookies:
            response.setCookie(name, value, **kw)
        response.setResult(b'test')
        return [header[1]
                for header in response.getHeaders()
                if header[0] == "Set-Cookie"]

    def testSetCookie(self):
        c = self._getCookieFromResponse([
                ('foo', 'bar', {}),
                ])
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c,
                        'foo=bar; not in %r' % c)

        c = self._getCookieFromResponse([
                ('foo', 'bar', {}),
                ('alpha', 'beta', {}),
                ])
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertTrue('alpha=beta;' in c or 'alpha=beta' in c)

        c = self._getCookieFromResponse([
                ('sign', u'\N{BIOHAZARD SIGN}', {}),
                ])
        self.assertTrue((r'sign="\342\230\243";' in c) or
                        (r'sign="\342\230\243"' in c))

        c = self._getCookieFromResponse([
                ('foo', 'bar', {
                    'Expires': 'Sat, 12 Jul 2014 23:26:28 GMT',
                    'domain': 'example.com',
                    'pAth': '/froboz',
                    'max_age': 3600,
                    'comment': u'blah;\N{BIOHAZARD SIGN}?',
                    'seCure': True,
                    }),
                ])[0]
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertTrue('expires=Sat, 12 Jul 2014 23:26:28 GMT;' in c, repr(c))
        self.assertTrue('Domain=example.com;' in c)
        self.assertTrue('Path=/froboz;' in c)
        self.assertTrue('Max-Age=3600;' in c)
        self.assertIn('Comment=', c)
        self.assertIn('blah%3B%E2%98%A3?', c)
        self.assertTrue('Secure' in c or 'secure' in c)

        c = self._getCookieFromResponse([('foo', 'bar', {'secure': False})])[0]
        self.assertTrue('foo=bar;' in c or 'foo=bar' in c)
        self.assertFalse('secure' in c)

    def test_handleException(self):
        response = p01.publisher.response.HTTPResponse()
        try:
            raise ValueError(1)
        except:
            exc_info = sys.exc_info()

        response.handleException(exc_info)
        self.assertEqual(response.getHeader("content-type"),
            "text/html;charset=utf-8")
        self.assertEqual(response.getStatus(), 500)
        self.assertTrue(response.consumeBody() in
             [b"<html><head>"
              b"<title>&lt;type 'exceptions.ValueError'&gt;</title></head>\n"
              b"<body><h2>&lt;type 'exceptions.ValueError'&gt;</h2>\n"
              b"A server error occurred.\n"
              b"</body></html>\n",
              b"<html><head><title>ValueError</title></head>\n"
              b"<body><h2>ValueError</h2>\n"
              b"A server error occurred.\n"
              b"</body></html>\n"]
             )

def cleanUp(test):
    zope.testing.cleanup.cleanUp()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHTTPResponse))
    return suite


if __name__ == '__main__':
    unittest.main()
