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
"""Publication test
"""

from __future__ import absolute_import
from builtins import object
import zope.interface
from zope.publisher.interfaces import Unauthorized
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import DebugError
from zope.publisher.publish import mapply

from p01.publisher import interfaces

##############################################################################
#
# dummy test component

class App(object):

    def __init__(self, name):
        self.name = name

    def index_html(self, request):
        return self


app = App('')
app.ZopeCorp = App('ZopeCorp')
app.ZopeCorp.Engineering = App('Engineering')


@zope.interface.implementer(interfaces.IPublication)
class DummyPublication(object):

    @property
    def app(self):
        """Return applicaiton"""
        return app

    def afterCall(self, request, ob):
        """See interface IPublication"""
        self._afterCall = getattr(self, '_afterCall', 0) + 1

    def endRequest(self, request, ob):
        """See interface IPublication"""
        self._endRequest = getattr(self, '_endRequest', 0) + 1

    def traverseName(self, request, ob, name, check_auth=1):
        """See interface IPublication"""
        return getattr(ob, name, "%s value" % name)

    def afterTraversal(self, request, ob):
        """See interface IPublication"""
        self._afterTraversal = getattr(self, '_afterTraversal', 0) + 1

    def beforeTraversal(self, request):
        """See interface IPublication"""
        self._beforeTraversal = getattr(self, '_beforeTraversal', 0) + 1

    def callObject(self, request, ob):
        """See interface IPublication"""
        return ob(request)

    def getApplication(self, request):
        """See interface IPublication"""
        return app

    def handleException(self, object, request, exc_info):
        """See interface IPublication"""
        try:
            request.response.setResult("%s: %s" % (exc_info[:2]))
        finally:
            exc_info = 0

    def callTraversalHooks(self, request, ob):
        """See interface IPublication"""
        self._callTraversalHooks = getattr(self, '_callTraversalHooks', 0) + 1


@zope.interface.implementer(interfaces.IPublication)
class DefaultPublication(object):
    """A stub publication.

    This works just like Zope2's ZPublisher. It rejects any name
    starting with an underscore and any objects (specifically: method)
    that doesn't have a docstring.
    """

    require_docstrings = True

    def __init__(self, app):
        self.app = app

    def startRequest(self, request):
        pass

    def beforeTraversal(self, request):
        # Lop off leading and trailing empty names
        stack = request.getTraversalStack()
        while stack and not stack[-1]:
            stack.pop() # toss a trailing empty name
        while stack and not stack[0]:
            stack.pop(0) # toss a leading empty name
        request.setTraversalStack(stack)

    def getApplication(self, request):
        return self.app

    def callTraversalHooks(self, request, ob):
        pass

    def traverseName(self, request, ob, name, check_auth=1):
        if name.startswith('_'):
            raise Unauthorized(name)
        if hasattr(ob, name):
            subob = getattr(ob, name)
        else:
            try:
                subob = ob[name]
            except (KeyError, IndexError,
                    TypeError, AttributeError):
                raise NotFound(ob, name, request)
        if self.require_docstrings and not getattr(subob, '__doc__', None):
            raise DebugError(subob, 'Missing or empty doc string')
        return subob

    def getDefaultTraversal(self, request, ob):
        return ob, ()

    def afterTraversal(self, request, ob):
        pass

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request, ob):
        pass

    def endRequest(self, request, ob):
        pass

    def handleException(self, object, request, exc_info):
        # Let the response handle it as best it can.
        request.response.reset()
        request.response.handleException(exc_info)


class TestPublication(DefaultPublication):

    def traverseName(self, request, ob, name, check_auth=1):
        if hasattr(ob, name):
            subob = getattr(ob, name)
        else:
            try:
                subob = ob[name]
            except (KeyError, IndexError,
                    TypeError, AttributeError):
                raise NotFound(ob, name, request)
        return subob
