#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''Bliss (BLiss IS SagaA) is a pragmatic, light-weight implementation of the OGF SAGA standard (GFD.90). The bliss.sagacompat module only exists to ensure B{compatibility} with existing SAGA implementations (U{http://www.saga-project.org}) and its use is B{highly discouraged}. Please use the bliss.saga module instead!
   
   More information can be found at: U{http://oweidner.github.com/bliss}
'''
__author__    = "Ole Christian Weidner"
__email__     = "ole.weidner@me.com"
__copyright__ = "Copyright 2011, Ole Christian Weidner"
__license__   = "MIT"

# Base "look-and-feel packages"
from bliss.saga._exception_impl import Exception as SException
class exception(SException):
    '''Loosely defines a SAGA Exception as defined in GFD.90.
    '''
    pass

from bliss.saga._exception_impl import Error as SError
class error(SError):
    '''Loosely defines a SAGA Error as defined in GFD.90.
    '''
    pass

from bliss.saga._object_impl import Object as SObject
class object(SObject):
    '''Loosely defines a SAGA Object as defined in GFD.90.
    '''
    pass

from bliss.saga._url_impl import Url as SUrl
class url(SUrl):
    '''Loosely defines a SAGA URL as defined in GFD.90.
    '''
    pass

from bliss.saga._session_impl import Session as SSession
class session(SSession):
    '''Loosely defines a SAGA Session as defined in GFD.90.
    '''
    pass

from bliss.saga._context_impl import Context as SContext
class context(SContext):
    '''Loosely defines a SAGA Context as defined in GFD.90.
    '''
    pass

# API packages
from bliss.saga           import filesystem
from bliss.saga           import job
from bliss.saga           import sd
  
