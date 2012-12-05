#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''This examples shows how list a directory on a LFC.

   If something doesn't work as expected, try to set 
   SAGA_VERBOSE=3 in your environment before you run the
   script in order to get some debug output.

   If you think you have encountered a defect, please 
   report it at: https://github.com/saga-project/bliss/issues
'''

__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2012, Mark Santcroos"
__license__   = "MIT"

import sys, time
import bliss.saga as saga

def main():
    
    try:
        mydir = saga.logicalfile.LogicalDirectory('irods:///osg/home/azebro1') 
        #mydir_wrong = saga.logicalfile.LogicalDirectory('lfn://lfc.grid.sara.nl:5010/grid/vlemed/mark/bliss-non-exist') 
        
        for entry in mydir.list():
            print entry

    except saga.Exception, ex:
        print "An error occured during file operation: %s" % (str(ex))
        sys.exit(-1)

    print "test script finished execution"

if __name__ == "__main__":
    main()
