#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''SAGA Job Package API.
'''

__author__    = "Ole Christian Weidner"
__email__     = "ole.weidner@me.com"
__copyright__ = "Copyright 2011, Ole Christian Weidner"
__license__   = "MIT"

from bliss.saga.filesystem._file_impl import File as SFile
class File(SFile):
    '''Loosely defines a SAGA File as defined in GFD.90.
    '''
    pass

from bliss.saga.filesystem._directory_impl import Directory as SDirectory
class Directory(SDirectory):
    '''Loosely defines a SAGA Directory as defined in GFD.90.
    '''
    pass

