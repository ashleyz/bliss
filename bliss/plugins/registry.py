#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ole Christian Weidner"
__email__     = "ole.weidner@me.com"
__copyright__ = "Copyright 2011, Ole Christian Weidner"
__license__   = "MIT"

from bliss.plugins.job import localjob

# Here is where the plugins are registered
_registry = []

_registry.append({"class"   : localjob.LocalJobPlugin,
                  "type"    : localjob.LocalJobPlugin.supported_api(),
                  "name"    : localjob.LocalJobPlugin.plugin_name(),
                  "schemas" : localjob.LocalJobPlugin.supported_schemas()})

