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
"""
$Id: interfaces.py 5279 2025-05-16 11:48:45Z roger.ineichen $
"""
from __future__ import absolute_import
from builtins import object
from zope.interface import implementer
__docformat__ = "reStructuredText"

import zope.interface
import zope.interface.interfaces
import zope.component.interfaces
import zope.location.interfaces
import zope.publisher.interfaces.browser

import p01.jsonrpc.interfaces


##############################################################################
#
# application

class IApplication(zope.location.interfaces.IRoot,
    zope.component.interfaces.ISite, zope.location.interfaces.ILocation):
    """Non ZODB application root. Does not provide IContainer"""


class IWSGIApplication(zope.interface.Interface):
    """A WSGI application"""

    def __call__(environ, start_response):
        """Called by a WSGI server.

        The ``environ`` parameter is a dictionary object, containing CGI-style
        environment variables. This object must be a builtin Python dictionary
        (not a subclass, UserDict or other dictionary emulation), and the
        application is allowed to modify the dictionary in any way it
        desires. The dictionary must also include certain WSGI-required
        variables (described in a later section), and may also include
        server-specific extension variables, named according to a convention
        that will be described below.

        The ``start_response`` parameter is a callable accepting two required
        positional arguments, and one optional argument. For the sake of
        illustration, we have named these arguments ``status``,
        ``response_headers``, and ``exc_info``, but they are not required to
        have these names, and the application must invoke the
        ``start_response`` callable using positional arguments
        (e.g. ``start_response(status, response_headers)``).
        """


##############################################################################
#
# request

class IBrowserRequest(zope.publisher.interfaces.browser.IBrowserRequest):
    """Browser request"""

    app = zope.interface.Attribute("""Application (root) object""")
    appURL = zope.interface.Attribute("""Application (root) URL""")

    def json():
        """Returns the json formatted content if application/json was used"""


class IJSONRPCRequest(p01.jsonrpc.interfaces.IJSONRPCRequest):
    """JSON-RPC request"""

    app = zope.interface.Attribute("""Application (root) object""")
    appURL = zope.interface.Attribute("""Application (root) URL""")


##############################################################################
#
# response

class IResponse(zope.interface.Interface):
    """Response without retry"""

    def setResult(result):
        """Sets the response result value.
        """

    def handleException(exc_info):
        """Handles an exception.

        This method is intended only as a convenience for the publication
        object.  The publication object can choose to handle exceptions by
        calling this method.  The publication object can also choose not
        to call this method at all.

        Implementations set the response body.
        """

    def internalError():
        """Called when the exception handler bombs.

        Should report back to the client that an internal error occurred.
        """

    def reset():
        """Reset the output result.

        Reset the response by nullifying already set variables.
        """


class IHTTPResponse(IResponse):
    """HTTP Response without authUser information"""

    def getStatus():
        """Returns the current HTTP status code as an integer.
        """

    def setStatus(status, reason=None):
        """Sets the HTTP status code of the response

        The status parameter must be either an integer (preferred), a value
        that can be converted to an integer using the int() function,
        or one of the standard status messages listed in the status_codes
        dict of the zope.publisher.http module (including "OK", "NotFound",
        and so on).  If the parameter is some other value, the status will
        be set to 500.

        The reason parameter is a short message to be sent with the status
        code to the client.  If reason is not provided, a standard
        reason will be supplied, falling back to "Unknown" for unregistered
        status codes.
        """

    def getStatusString():
        """Return the status followed by the reason."""

    def setHeader(name, value, literal=False):
        """Sets an HTTP return header "name" with value "value"

        The previous value is cleared. If the literal flag is true,
        the case of the header name is preserved, otherwise
        word-capitalization will be performed on the header name on
        output.
        """

    def addHeader(name, value):
        """Add an HTTP Header

        Sets a new HTTP return header with the given value, while retaining
        any previously set headers with the same name.
        """

    def getHeader(name, default=None):
        """Gets a header value

        Returns the value associated with a HTTP return header, or
        'default' if no such header has been set in the response
        yet.
        """

    def getHeaders():
        """Returns a list of header name, value tuples.
        """

    def appendToCookie(name, value):
        """Append text to a cookie value

        If a value for the cookie has previously been set, the new
        value is appended to the old one separated by a colon.
        """

    def expireCookie(name, **kw):
        """Causes an HTTP cookie to be removed from the browser

        The response will include an HTTP header that will remove the cookie
        corresponding to "name" on the client, if one exists. This is
        accomplished by sending a new cookie with an expiration date
        that has already passed. Note that some clients require a path
        to be specified - this path must exactly match the path given
        when creating the cookie. The path can be specified as a keyword
        argument.
        If the value of a keyword argument is None, it will be ignored.
        """

    def setCookie(name, value, **kw):
        """Sets an HTTP cookie on the browser

        The response will include an HTTP header that sets a cookie on
        cookie-enabled browsers with a key "name" and value
        "value". This overwrites any previously set value for the
        cookie in the Response object.
        If the value of a keyword argument is None, it will be ignored.
        """

    def getCookie(name, default=None):
        """Gets HTTP cookie data as a dict

        Returns the dict of values associated with an HTTP cookie set in the
        response, or 'default' if no such cookie has been set in the response
        yet.
        """

    def setResult(result):
        """Sets response result value based on input.

        Input is usually a unicode string, a string, None, or an object
        that can be adapted to IResult with the request.  The end result
        is an iterable such as WSGI prefers, determined by following the
        process described below.

        Try to adapt the given input, with the request, to IResult
        (found above in this file).  If this fails, and the original
        value was a string, use the string as the result; or if was
        None, use an empty string as the result; and if it was anything
        else, raise a TypeError.

        If the result of the above (the adaptation or the default
        handling of string and None) is unicode, encode it (to the
        preferred encoding found by adapting the request to
        zope.i18n.interfaces.IUserPreferredCharsets, usually implemented
        by looking at the HTTP Accept-Charset header in the request, and
        defaulting to utf-8) and set the proper encoding information on
        the Content-Type header, if present.  Otherwise (the end result
        was not unicode) application is responsible for setting
        Content-Type header encoding value as necessary.

        If the result of the above is a string, set the Content-Length
        header, and make the string be the single member of an iterable
        such as a tuple (to send large chunks over the wire; see
        discussion in the IResult interface).  Otherwise (the end result
        was not a string) application is responsible for setting
        Content-Length header as necessary.

        Set the result of all of the above as the response's result. If
        the status has not been set, set it to 200 (OK). """

    def consumeBody():
        """Returns the response body as a string.

        Note that this function can be only requested once, since it is
        constructed from the result.
        """

    def consumeBodyIter():
        """Returns the response body as an iterable.

        Note that this function can be only requested once, since it is
        constructed from the result.
        """

    def redirect(location, status=302, trusted=False):
        """Causes a redirection without raising an error.

        By default redirects are untrusted which restricts target URLs to the
        same host that the request was sent to.

        If the `trusted` flag is set, redirects are allowed for any target
        URL.

        """


class IBrowserResponse(IHTTPResponse):
    """HTTP response for browser request"""


class IJSONRPCResponse(IHTTPResponse):
    """HTTP response for jsonrpc request"""


##############################################################################
#
# publication

class IPublication(zope.publisher.interfaces.IPublication):
    """Response"""

    def handleException(object, request, exc_info):
        """Handle an exception (without retry option)

        Either:
        - sets the body of the response, request.response, or
        - raises a Retry exception, or
        - throws another exception, which is a Bad Thing.
        """

class IBrowserPublication(IPublication,
    zope.publisher.interfaces.browser.IBrowserPublication):
    """Bowser publication."""

    def startRequest(self, request):
        """Start new interaction and beginn transaction.

        This new hook allows us to prepare everything and handle
        request.processInputs with transaction control.
        """


class IJSONRPCPublication(IPublication,
    p01.jsonrpc.interfaces.IJSONRPCPublication):
    """JSON-RPC publication."""

    def startRequest(self, request):
        """Start new interaction and beginn transaction.

        This new hook allows us to prepare everything and handle
        request.processInputs with transaction control.
        """


# Remove this left over from zope.app.publication
#class IFileContent(zope.interface.Interface):
#    """Marker interface for content that can be managed as files.
#
#    The default view for file content has effective URLs that don't end in
#    `/`.  In particular, if the content included HTML, relative links in
#    the HTML are relative to the container the content is in.
#    """


##############################################################################
#
# events

class IApplicationCreatedEvent(zope.interface.interfaces.IObjectEvent):

    app = zope.interface.Attribute(u"IApplication")


@implementer(IApplicationCreatedEvent)
class ApplicationCreatedEvent(object):


    def __init__(self, application):
        self.object = application


class IWSGIApplicationCreatedEvent(zope.interface.interfaces.IObjectEvent):

    app = zope.interface.Attribute(u"IWSGIApplication")


@implementer(IWSGIApplicationCreatedEvent)
class WSGIApplicationCreatedEvent(object):


    def __init__(self, application):
        self.object = application


##############################################################################
#
# publisher

class IPublisherRegistry(zope.interface.Interface):
    """Publisher factory registry

    A registry to lookup a PublisherFactory by request method + mime-type.
    Multiple factories can be configured for the same method+mimetype.
    Factories are sorted in the order of their registration in ZCML.
    """

    def register(method, mimetype, name, priority, factory):
        """Registers a factory for method+mimetype."""

    def lookup(method, mimetype, environment):
        """Lookup a factory for a given method+mimetype and a
        environment.
        """

    def getFactoriesFor(method, mimetype):
        """Return the internal datastructure representing the configured
        factories (basically for testing, not for introspection).
        """


class IPublisherFactory(zope.interface.Interface):
    """Publisher factory stored in the publisher registry"""

    def __call__():
        """Return a tuple (request, publication)"""


class IPublisher(zope.interface.Interface):
    """IPublisher registry"""

    def __call__(input_stream, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a cached publication instance.
        """

    def publish(request):
        """Publish a request"""
