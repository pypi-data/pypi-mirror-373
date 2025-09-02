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
"""Zope conf product configuration.

"""
from __future__ import absolute_import

import os.path
from builtins import object

import ZConfig

_configs = {}
_schema = None


def getProductConfiguration(name):
    """Return the product configuration for product `name`.

    If there is no configuration for `name`, None is returned.

    """
    return _configs.get(name)


def setProductConfigurations(configs):
    """Initialize product configuration from ZConfig data."""
    pconfigs = {}
    for pconfig in configs:
        pconfigs[pconfig.getSectionName()] = pconfig.mapping
    _configs.clear()
    _configs.update(pconfigs)


def setProductConfiguration(name, mapping):
    """Set the configuration for a single product."""
    if mapping is None:
        if name in _configs:
            del _configs[name]
    else:
        _configs[name] = mapping


def saveConfiguration():
    """Retrieve a shallow copy of the configuration state."""
    return _configs.copy()


def restoreConfiguration(state):
    """Restore the configuration state based on a state value."""
    _configs.clear()
    _configs.update(state)


def loadConfiguration(file, url=None):
    global _schema
    if _schema is None:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "schema", "productconfig.xml")
        _schema = ZConfig.loadSchema(path)
    data, handlers = ZConfig.loadConfigFile(_schema, file, url=url)
    return dict((sect.getSectionName(), sect.mapping)
                for sect in data.product_config)


class FauxConfiguration(object):
    """Configuration object that can be use from tests.

    An instance is of this is similar to a <product-config> section from a
    zope.conf file in all the ways this module cares about.

    """

    def __init__(self, name, mapping):
        self.name = name
        self.mapping = dict(mapping)

    def getSectionName(self):
        return self.name

try:
    import zope.testing.cleanup
except ImportError:
    pass
else:
    zope.testing.cleanup.addCleanUp(_configs.clear)
