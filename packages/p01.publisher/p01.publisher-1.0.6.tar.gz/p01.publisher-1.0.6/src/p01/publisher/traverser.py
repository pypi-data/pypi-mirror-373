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
"""Object traversers

$Id: traverser.py 5167 2025-03-06 00:11:40Z felipe.souza $
"""
from __future__ import absolute_import
from builtins import object
from zope.interface import implementer
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
import zope.component.interfaces
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import IAuthentication
from zope.security.proxy import removeSecurityProxy

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.defaultview import getDefaultViewName


class AuthenticationMixin(object):
    """Traverser used for authentication call

    Our ZODB based Publication doesn't provide _maybePlacefullyAuthenticate and
    doesn't try to authenticate on each traversed object. This means ou need to
    inherit from this mixin class for authentication placefull support.
    """

    def doPlacefullyAuthenticate(self, ob, request):
        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            # We've already got an authenticated user. There's nothing to do.
            # Note that beforeTraversal guarentees that user is not None.
            return

        if not zope.component.interfaces.ISite.providedBy(ob):
            # We won't find an authentication utility here, so give up.
            return

        sm = removeSecurityProxy(ob).getSiteManager()
        auth = sm.queryUtility(IAuthentication)
        if auth is None:
            # No auth utility here
            return

        # Try to authenticate against the auth utility
        principal = auth.authenticate(request)
        if principal is None:
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # nothing to do here
                return

        request.setPrincipal(principal)


@implementer(IBrowserPublisher)
class ItemTraverser(object):
    """Browser traverser for simple components that can only traverse to views
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        if request.method == 'OPTIONS':
            # support OPTIONS CORS preflight and use OPTIONS view
            viewName = 'OPTIONS'
        else:
            viewName = getDefaultViewName(self.context, request)
        return self.context, (viewName,)

    def publishTraverse(self, request, name):
        view = zope.component.queryMultiAdapter((self.context, request),
            name=name)
        if view is None:
            raise NotFound(self.context, name)
        return view


@implementer(IBrowserPublisher)
class ContainerTraverser(object):
    """Browser traverser for containers that can traverse to views and items

    NOTE: views get traversed before items. Make sure your views don't use the
    same name as your items! or make sure that @@ get used as view name prefix.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        if request.method == 'OPTIONS':
            # support OPTIONS CORS preflight and use OPTIONS view
            viewName = 'OPTIONS'
        else:
            viewName = getDefaultViewName(self.context, request)
        return self.context, (viewName,)

    def publishTraverse(self, request, name):

        # Note: we changed the order of lookup because we do not like to
        # force the storage to lookup MongoDB if we need a view. But take
        # care, this means a view name will override a item key if you don't
        # use a @@ view marker prefix.
        view = zope.component.queryMultiAdapter((self.context, request),
            name=name)
        if view is not None:
            return view

        # container item lookup
        try:
            return self.context[name]
        except KeyError:
            pass

        raise NotFound(self.context, name)


class FileContentTraverser(ItemTraverser):
    """Browser traverser for file content.

    The default view for file content has effective URLs that don't end in
    /.  In particular, if the content inclused HTML, relative links in
    the HTML are relative to the container the content is in.
    """

    def browserDefault(self, request):
        viewName = getDefaultViewName(self.context, request)
        view = self.publishTraverse(request, viewName)
        if hasattr(view, 'browserDefault'):
            if request.method == 'OPTIONS':
                # support OPTIONS CORS preflight and use OPTIONS view
                viewName = 'OPTIONS'
            else:
                view, path = view.browserDefault(request)
            if len(path) == 1:
                view = view.publishTraverse(request, path[0])
                path = ()
        else:
            path = ()

        return view, path


class SiteTraverser(AuthenticationMixin, ContainerTraverser):
    """Site traverser including placefull authentication"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doPlacefullyAuthenticate(context, request)


def NoTraverser(ob, request):
    return None
