#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''This examples shows how to use the saga.Filesystem API

   If something doesn't work as expected, try to set 
   SAGA_VERBOSE=3 in your environment before you run the
   script in order to get some debug output.

   If you think you have encountered a defect, please 
   report it at: https://github.com/saga-project/bliss/issues
'''

__author__    = "Ole Christian Weidner"
__copyright__ = "Copyright 2011-2012, Ole Christian Weidner"
__license__   = "MIT"

import sys, time
import bliss.saga as saga

def main():
    
    try:
        # Optional:
        # Set up a security context
        # if no security context is defined, the SFTP
        # plugin will pick up the default set of ssh 
        # credentials of the user, i.e., ~/.ssh/id_rsa
        #
        #ctx = saga.Context()
        #ctx.type = saga.Context.SSH
        #ctx.userid  = 'loginname' # like 'ssh username@host ...'
        #ctx.userkey = '/home/you/.ssh/id_rsa_custom' # like ssh -i ...'
   
        # Optional:  
        # Append the custom security context to the session
        #session = saga.Session()
        #session.contexts.append(ctx)
 
        # open home directory on a remote machine
        remote_dir = saga.filesystem.Directory('sftp://india.futuregrid.org/etc/')
        # Alternatively: 
        # Use custom session to create Directory object
        #remote_dir = saga.filesystem.Directory('sftp://queenbee.loni.org/etc/', 
        #                                  session=session)

        # copy .bash_history to /tmp/ on the local machine
        remote_dir.copy('hosts', 'sftp://localhost/tmp/') 

        # list 'h*' in local /tmp/ directory
        local_dir = saga.filesystem.Directory('sftp://localhost/tmp/')
        print local_dir.list(pattern='h*')

    except saga.Exception, ex:
        print "An error occured during file operation: %s" % (str(ex))
        sys.exit(-1)

if __name__ == "__main__":
    main()
