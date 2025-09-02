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
$Id: application.py 5625 2025-08-26 11:44:03Z roger.ineichen $
"""
from __future__ import absolute_import
from __future__ import print_function
from builtins import str
from builtins import object
import os
import sys
import time
import logging
import ZConfig
import zope.interface
import zope.component
import zope.event
import zope.processlifetime

import p01.publisher.publisher
import p01.publisher.appsetup
import p01.publisher.product
from p01.publisher import interfaces


@zope.interface.implementer(interfaces.IApplication)
class Application(object):
    """Application (root) class for ZODB less publications"""

    __name__ = __parent__ = None

    def __init__(self):
        self.start_time = time.time()

    def getStartTime(self):
        return self.start_time

    def getSiteManager(self):
        return zope.component.getGlobalSiteManager()

    def setSiteManager(self, sm):
        raise NotImplementedError("setSiteManager is not supported")

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)


@zope.interface.implementer(interfaces.IWSGIApplication)
class WSGIApplication(object):
    """A WSGI application implementation for the zope publisher

    Instances of this class can be used as a WSGI application object.

    The class relies on a properly initialized request factory.
    """

    def __init__(self, app, publisher=p01.publisher.publisher.Publisher,
        handleErrors=True):
        self.app = app
        self.publisher = publisher(app)
        self.handleErrors = handleErrors

    def __call__(self, environ, start_response):
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
        request = self.publisher(environ['wsgi.input'], environ)

        # support post-mortem debugging
        handleErrors = environ.get('wsgi.handleErrors', self.handleErrors)

        # publish request and get response
        request = self.publisher.publish(request, handleErrors=handleErrors)
        response = request.response

        # Start the WSGI server response
        start_response(response.getStatusString(), response.getHeaders())

        # return the result body iterable (supports server side events)
        return response.consumeBodyIter()


class PMDBWSGIApplication(WSGIApplication):
    """Post mortem debugger wsgi application"""

    def __call__(self, environ, start_response):
        environ['wsgi.handleErrors'] = False

        # Call the application to handle the request and write a response
        try:
            app = super(PMDBWSGIApplication, self)
            return app.__call__(environ, start_response)
        except Exception as error:
            import sys, pdb
            print("%s:" % sys.exc_info()[0])
            print(sys.exc_info()[1])
            #import zope.security.management
            #zope.security.management.restoreInteraction()
            try:
                pdb.post_mortem(sys.exc_info()[2])
                raise
            finally:
                pass #zope.security.management.endInteraction()


def config(configfile, schemafile, features=()):
    # load the configuration schema file
    schema = ZConfig.loadSchema(schemafile)

    # load the configuration file
    try:
        options, handlers = ZConfig.loadConfig(schema, configfile)
    except ZConfig.ConfigurationError as msg:
        sys.stderr.write("Error: %s\n" % str(msg))
        sys.exit(2)

    # insert all specified python paths
    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]

    # parse product configs
    p01.publisher.product.setProductConfigurations(
        options.product_config)

    # setup the event log
    options.eventlog()

    # insert the devmode feature, if turned on
    if options.devmode:
        features += ('devmode',)
        logging.warning("Developer mode is enabled: this is a security risk "
            "and should NOT be enabled on production servers. Developer mode "
            "can usually be turned off by setting the `devmode` option to "
            "`off` or by removing it from the instance configuration file "
            "completely.")

    # execute the ZCML configuration.
    p01.publisher.appsetup.config(options.site_definition, features=features)


def getWSGIApplication(configfile, schemafile=None, features=(),
    publisher=p01.publisher.publisher.Publisher, handleErrors=True):
    # config based on paste.conf which includeds paste.zcml
    config(configfile, schemafile, features)
    app = zope.component.getUtility(interfaces.IApplication)

    wsgi = WSGIApplication(app, publisher, handleErrors)

    # create the application, notify subscribers.
    zope.event.notify(interfaces.ApplicationCreatedEvent(app))
    zope.event.notify(interfaces.WSGIApplicationCreatedEvent(wsgi))

    return wsgi


################################################################################
#
# ZODB wsgi application

def zodb_config(configfile, schemafile, features=()):
    # load the configuration schema file
    schema = ZConfig.loadSchema(schemafile)

    # load the configuration file
    try:
        options, handlers = ZConfig.loadConfig(schema, configfile)
    except ZConfig.ConfigurationError as msg:
        sys.stderr.write("Error: %s\n" % str(msg))
        sys.exit(2)

    # insert all specified python paths
    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]

    # parse product configs
    p01.publisher.product.setProductConfigurations(
        options.product_config)

    # setup the event log
    options.eventlog()

    # insert the devmode feature, if turned on
    if options.devmode:
        features += ('devmode',)
        logging.warning("Developer mode is enabled: this is a security risk "
            "and should NOT be enabled on production servers. Developer mode "
            "can usually be turned off by setting the `devmode` option to "
            "`off` or by removing it from the instance configuration file "
            "completely.")

    # execute the ZCML configuration.
    p01.publisher.appsetup.config(options.site_definition, features=features)
    # Connect to and open the database, notify subscribers.
    db = p01.publisher.appsetup.multi_database(options.databases)[0][0]
    zope.event.notify(zope.processlifetime.DatabaseOpened(db))
    return db


def getZODBApplication(configfile, schemafile=None, features=(),
    publisher=p01.publisher.publisher.Publisher, handleErrors=True):
    # config based on paste.conf which includeds paste.zcml
    db = zodb_config(configfile, schemafile, features)
    # setup wsgi application based on ZODB database
    wsgi = WSGIApplication(db, publisher, handleErrors)
    # create the application, notify subscribers.
    zope.event.notify(interfaces.WSGIApplicationCreatedEvent(wsgi))
    return wsgi
