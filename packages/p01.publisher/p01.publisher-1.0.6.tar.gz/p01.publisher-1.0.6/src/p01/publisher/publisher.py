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
"""Publisher

$Id: publisher.py 5279 2025-05-16 11:48:45Z roger.ineichen $
"""
from __future__ import absolute_import
from builtins import object
from zope.interface import implementer
import six
__docformat__ = "reStructuredText"

import sys

import zope.interface
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin

import p01.publisher.request
import p01.publisher.publication
from p01.publisher import interfaces
from p01.publisher.registry import chooseClasses


def publish(request, handleErrors=True):
    """Publish stack, see IPublisher for details"""
    try:
        # finally to clean up to_raise and close request
        to_raise = None
        # get publication
        obj = None
        publication = request.publication
        try:
            # start transaction
            publication.startRequest(request)
            # process input stream
            request.processInputs()
            # notify traversal start
            publication.beforeTraversal(request)
            # get application
            obj = publication.getApplication(request)
            # traverse
            obj = request.traverse(obj)
            # process object (page)
            result = publication.callObject(request, obj)
            # get response and result
            response = request.response
            if result is not response:
                response.setResult(result)
            # notify after call
            publication.afterCall(request, obj)
        except:
            # handle publication error
            exc_info = sys.exc_info()
            try:
                publication.handleException(obj, request, exc_info)
            except:
                # bad exception handler handling exception, make sure this
                # never happens! But if so make sure internalError method
                # knows whats to do
                request.response.internalError()
                to_raise = sys.exc_info()
            if not handleErrors:
                # wsgi.handleError = False means the zope publisher
                # should handle errors and don't dispatch them to
                # wsgi. In case zope should not handle error just
                # raise it here. This is only used for testing
                raise
        finally:
            publication.endRequest(request, obj)

        response = request.response
        if to_raise is not None:
            # raise not catched exceptions
            six.reraise(to_raise[0], to_raise[1], to_raise[2])

    finally:
        # avoid circ. ref.
        to_raise = None
        # close request and cleanup hooks in request._held
        request.close()

    # return the request
    return request


def debug_call(obj, args):
    # The presence of this function allows us to set a pdb breakpoint
    return obj(*args)


@zope.interface.implementer(interfaces.IPublisher)
class Publisher(object):
    """Publisher shared per wsgi application

    A Publisher knows how to get the right request class based on a given
    environment. The publisher is also responsible for setup the right skin.
    """

    def __init__(self, app, handleErrors=False):
        self._app = app
        self._handleErrors = handleErrors
        self._cache = {}

    def __call__(self, input_stream, env):
        """Lookup request and publication class based on given request"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env)

        # get publication (singleton per request type)
        publication = self._cache.get(publication_class)
        if publication is None:
            publication = publication_class(self._app)
            self._cache[publication_class] = publication

        # setup request
        request = request_class(input_stream, env)
        request.setPublication(publication)
        if ISkinnable.providedBy(request):
            # only ISkinnable requests have skins
            setDefaultSkin(request)
        return request

    def publish(self, request, handleErrors=None):
        # use handleErrors if not None or default (self._handleErrors)
        return publish(request, handleErrors or self._handleErrors)


###############################################################################
#
# publisher factory helper

@implementer(interfaces.IPublisherFactory)
class PublisherFactoryBase(object):
    """Publisher factory which returns the right request/publication"""


    def __init__(self, requestClass=None, publicationClass=None):
        if requestClass is not None:
            self.requestClass = requestClass
        if publicationClass is not None:
            self.publicationClass = publicationClass

    def canHandle(self, environment):
        return True

    def __call__(self):
        return self.requestClass, self.publicationClass


# browser
class BrowserFactory(PublisherFactoryBase):
    """Browser publisher factory which returns the right request/publication"""

    requestClass = p01.publisher.request.BrowserRequest
    publicationClass = p01.publisher.publication.BrowserPublication


class BrowserZODBFactory(PublisherFactoryBase):
    """Browser publisher factory which returns the right request/publication"""

    requestClass = p01.publisher.request.BrowserRequest
    publicationClass = p01.publisher.publication.BrowserZODBPublication


# jsonrpc
class JSONRPCFactory(PublisherFactoryBase):
    """JSON-RPC publisher factory which returns the right request/publication"""

    requestClass = p01.publisher.request.JSONRPCRequest
    publicationClass = p01.publisher.publication.JSONRPCPublication


class JSONRPCZODBFactory(PublisherFactoryBase):
    """JSON-RPC publisher factory which returns the right request/publication"""

    requestClass = p01.publisher.request.JSONRPCRequest
    publicationClass = p01.publisher.publication.JSONRPCZODBPublication