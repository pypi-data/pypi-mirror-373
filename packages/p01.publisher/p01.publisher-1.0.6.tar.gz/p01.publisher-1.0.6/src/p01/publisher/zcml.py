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
"""Publisher factory directive

$Id: zcml.py 5167 2025-03-06 00:11:40Z felipe.souza $
"""
from __future__ import absolute_import
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema
import zope.configuration.fields

from p01.publisher.registry import registry


class IPublisherFactoryDirective(zope.interface.Interface):
    """Link a request type to a request and publication factory"""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the publication factory.')

    factory = zope.configuration.fields.GlobalObject(
        title=u'Factory',
        description=u'The request-publication factory')

    methods = zope.configuration.fields.Tokens(
        title=u'Methods',
        description=(u'A list of HTTP method names. If the method is a "*", '
                     u'then all methods will match. Example: "GET POST"'),
        value_type=zope.schema.TextLine(),
        required=False)

    mimetypes = zope.configuration.fields.Tokens(
        title=u'Mime Types',
        description=(u'A list of content/mime types of the request. If the '
                     u'type is a "*" then all types will be matched. '
                     u'Example: "text/html text/xml"'),
        value_type=zope.schema.TextLine(),
        required=False)

    priority = zope.schema.Int(
        title=u'Priority',
        description=(u'A priority key used to concurrent'
                     ' publication factories.'),
        required=False)

    request = zope.configuration.fields.GlobalObject(
        title=u'Request class',
        description=u'Request class',
        required=False)

    publication = zope.configuration.fields.GlobalObject(
        title=u'Publication class',
        description=u'Publication class',
        required=False)


def publisher(_context, name, factory, methods=['*'], mimetypes=['*'],
    priority=0, request=None, publication=None):

    if request is not None or publication is not None:
        factory = factory(request, publication)
    else:
        factory = factory()

    for method in methods:
        for mimetype in mimetypes:
            _context.action(
                discriminator = (method, mimetype, priority),
                callable = registry.register,
                args = (method, mimetype, name, priority, factory)
                )
