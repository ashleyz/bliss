#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ole Christian Weidner"
__copyright__ = "Copyright 2011, Ole Christian Weidner"
__license__   = "MIT"

# Using urlparse from Python 2.5
from bliss.utils       import urlparse25 as urlparse  
from bliss.saga.Object import Object 

class Url(Object):
    '''Defines a SAGA Url class as defined in GFD.90.'''

    #__slots__ = ('_urlobj', 'scheme', 'host', 'port', 'path', 'params', 'query', 'fragment', 'url')

    def __init__(self, urlstring=''):
        '''Construct a new Url from a string'''

        Object.__init__(self, objtype=Object.Type.Url, apitype=Object.Type.BaseAPI)

        self._urlobj  = urlparse.urlparse(urlstring)
         
        self.scheme   = self._urlobj.scheme
        '''The scheme part of the Url.'''
        self.host     = self._urlobj.hostname #host
        '''The host part of the Url.'''

        if self._urlobj.port is not None:
            self.port = int(self._urlobj.port) # int(port)
            '''The port part of the Url.'''
        else:
            self.port = None

        '''The port part of the Url.'''
        self.username = self._urlobj.username
        '''The username part of the Url.'''
        self.password = self._urlobj.password
        '''The password part of the Url.'''
        self.path     = self._urlobj.path
        '''The path part of the Url.'''
        self.query    = self._urlobj.query
        '''The query part of the Url.'''
        self.fragment = self._urlobj.fragment
        '''The fragment part of the Url.'''
        self.url      = str(self._urlobj.geturl())
        '''The Url as string (same as __str__).'''

    # Old-style accessors
    def __del__(self):
        '''Destructor (tear-down the Url object).'''

    def __str__(self):
        '''Return Url as string.'''
        return self.url

    def get_scheme(self):
        '''return the 'scheme' property.'''
        return self.scheme

    def set_scheme(self, val):
        '''set the 'scheme' property.'''
        self.scheme = val

    def get_host(self):
        '''return the 'host' property.'''
        return self.host

    def set_host(self, val):
        '''set the 'host' property.'''
        self.host = val

    def get_port(self):
        '''return the 'port' property.'''
        return self.port

    def set_port(self, port):
        '''set the 'port' property.'''
        self.port = val

    def get_fragment(self):
        '''return the 'fragment' property.'''
        return self.fragment

    def set_fragment(self, val):
        '''set the 'fragment' property.'''
        self.fragment = val

    def get_path(self):
        '''return the 'path' property.'''
        return self.path

    def set_path(self, val):
        '''set the 'path' property.'''
        self.path = val

    def get_query(self):
        '''return the 'query' property.'''
        return self.quey

    def set_query(self, query):
        '''set the 'query' property.'''
        self.query = val

    def get_username(self):
        '''return the 'username' property.'''
        return self.username

    def set_username(self, val):
        '''set the 'username' property.'''
        self.username = val

    def get_password(self):
        '''return the 'username' property.'''
        return self.username

    def set_password(self, val):
        '''set the 'password' property.'''
        self.password = val

