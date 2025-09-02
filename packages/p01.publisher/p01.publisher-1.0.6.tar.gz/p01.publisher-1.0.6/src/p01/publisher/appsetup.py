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
"""Code to initialize the application server

$Id: appsetup.py 5435 2025-07-02 14:10:13Z rodrigo.ristow $
"""
from builtins import object

import zope.component
import zope.component.hooks
import zope.interface
from zope.interface import implementer
from zope.security.interfaces import IParticipation
from zope.security.management import system_user


@implementer(IParticipation)
class SystemConfigurationParticipation(object):

    principal = system_user
    interaction = None


_configured = False
def config(file, features=(), execute=True):
    r"""Execute the ZCML configuration file.

    This procedure defines the global site setup. Optionally you can also
    provide a list of features that are inserted in the configuration context
    before the execution is started.

    Let's create a trivial sample ZCML file.

      >>> import tempfile
      >>> fn = tempfile.mktemp('.zcml')
      >>> zcml = open(fn, 'w')
      >>> zcml.write('''
      ... <configure xmlns:meta="http://namespaces.zope.org/meta"
      ...            xmlns:zcml="http://namespaces.zope.org/zcml">
      ...   <meta:provides feature="myFeature" />
      ...   <configure zcml:condition="have myFeature2">
      ...     <meta:provides feature="myFeature4" />
      ...   </configure>
      ... </configure>
      ... ''')
      >>> zcml.close()

    We can now pass the file into the `config()` function:

      # End an old interaction first
      >>> from zope.security.management import endInteraction
      >>> endInteraction()

      >>> context = config(fn, features=('myFeature2', 'myFeature3'))
      >>> context.hasFeature('myFeature')
      True
      >>> context.hasFeature('myFeature2')
      True
      >>> context.hasFeature('myFeature3')
      True
      >>> context.hasFeature('myFeature4')
      True

    Further, we should have access to the configuration file name and context
    now:

      >>> getConfigSource() is fn
      True
      >>> getConfigContext() is context
      True

    Let's now clean up by removing the temporary file:

      >>> import os
      >>> os.remove(fn)

    """
    global _configured
    global __config_source
    __config_source = file

    if _configured:
        return

    from zope.configuration import xmlconfig, config

    # Set user to system_user, so we can do anything we want
    from zope.security.management import newInteraction
    newInteraction(SystemConfigurationParticipation())

    # Hook up custom component architecture calls
    zope.component.hooks.setHooks()

    # Load server-independent site config
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    for feature in features:
        context.provideFeature(feature)
    context = xmlconfig.file(file, context=context, execute=execute)

    # Reset user
    from zope.security.management import endInteraction
    endInteraction()

    _configured = execute

    global __config_context
    __config_context = context

    return context


def multi_database(database_factories):
    """Set up a multi-database from an iterable of database factories

    Return a sequence of databases, and a mapping of from database name to
    database.

    >>> class DB:
    ...     def __init__(self, number):
    ...         self.number = number
    ...     def __repr__(self):
    ...         return "DB(%s)" % self.number
    ...     def getActivityMonitor(self):
    ...         return self._activity_monitor
    ...     def setActivityMonitor(self, am):
    ...         self._activity_monitor = am

    >>> class Factory:
    ...     def __init__(self, name, number):
    ...         self.name = name
    ...         self.number = number
    ...     def open(self):
    ...         return DB(self.number)

    >>> s, m = multi_database(
    ...           [Factory(None, 3), Factory('y', 2), Factory('x', 1)])

    >>> list(s)
    [DB(3), DB(2), DB(1)]

    >>> [d.database_name for d in s]
    ['', 'y', 'x']

    >>> [d.databases is m for d in s]
    [True, True, True]

    >>> items = m.items()
    >>> sorted(list(items))
    [('', DB(3)), ('x', DB(1)), ('y', DB(2))]

    Each of the databases is registered as an IDatabase utility:

    >>> from zope import component
    >>> [(component.getUtility(ZODB.interfaces.IDatabase, name) is m[name])
    ...  for name in m]
    [True, True, True]

    And has an activity monitor:

    >>> [isinstance(db.getActivityMonitor(),
    ...             ZODB.ActivityMonitor.ActivityMonitor)
    ...  for db in m.values()]
    [True, True, True]

    """
    # lazy import (ZODB dependency)
    import ZODB.ActivityMonitor
    import ZODB.interfaces
    databases = {}
    result = []
    for factory in database_factories:
        name = factory.name or ''
        if name in databases:
            raise ValueError("Duplicate database name: %r" % name)
        db = factory.open()
        db.databases = databases
        db.database_name = name
        databases[name] = db
        # Grrr bug in ZODB. Database doesn't declare that it implements
        # IDatabase.
        if not ZODB.interfaces.IDatabase.providedBy(db):
            zope.interface.directlyProvides(db, ZODB.interfaces.IDatabase)
        zope.component.provideUtility(db, ZODB.interfaces.IDatabase, name)
        db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())
        result.append(db)

    return result, databases


__config_context = None
def getConfigContext():
    return __config_context

__config_source = None
def getConfigSource():
    return __config_source

def reset():
    global _configured
    _configured = False

    global __config_source
    __config_source = None

    global __config_context
    __config_context = None

try:
    import zope.testing.cleanup
except ImportError:
    pass
else:
    zope.testing.cleanup.addCleanUp(reset)
