# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ole Christian Weidner"
__copyright__ = "Copyright 2011-2012, Ole Christian Weidner"
__license__   = "MIT"

_registry = []

_registry.append({"module"   : "bliss.plugins.local.localjob",  "class" : "LocalJobPlugin"})
_registry.append({"module"   : "bliss.plugins.ssh.job",         "class" : "SSHJobPlugin"})
_registry.append({"module"   : "bliss.plugins.sftp.sftpfile",   "class" : "SFTPFilesystemPlugin"})
_registry.append({"module"   : "bliss.plugins.sge.sgesshjob",   "class" : "SGEJobPlugin"})
_registry.append({"module"   : "bliss.plugins.pbs.pbsshjob",    "class" : "PBSJobPlugin"})

from bliss.plugins.lfc import lfclogicalfile
_registry.append({"module"    : "bliss.plugins.lfc.lfclogicalfile", "class" : "LFCLogicalFilePlugin"})
_registry.append({"module"    : "bliss.plugins.irods.irodslogicalfile", "class" : "iRODSLogicalFilePlugin"})
#_registry.append({"class"   : LFCLogicalFilePlugin,
#                  "apis"    : LFCLogicalFilePlugin.supported_apis(),
#                  "name"    : LFCLogicalFilePlugin.plugin_name(),
#                  "schemas" : LFCLogicalFilePlugin.supported_schemas()})

