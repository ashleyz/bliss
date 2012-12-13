#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''This example runs some iRODS commands

   If something doesn't work as expected, try to set 
   SAGA_VERBOSE=3 in your environment before you run the
   script in order to get some debug output.

   If you think you have encountered a defect, please 
   report it at: https://github.com/saga-project/bliss/issues
'''

__author__    = "Ashley Zebrowski"
__copyright__ = "Copyright 2012, Ashley Zebrowski"
__license__   = "MIT"

import sys, time
import bliss.saga as saga

def main():
    
    try:
        print "Creating iRODS directory object"
        mydir = saga.logicalfile.LogicalDirectory('irods:///osg/home/azebro1') 
        #mydir_wrong = saga.logicalfile.LogicalDirectory('lfn://lfc.grid.sara.nl:5010/grid/vlemed/mark/bliss-non-exist') 

        print "Printing results"
        
        for entry in mydir.list():
            print entry

        myfile = saga.logicalfile.LogicalFile('irods:///osg/home/azebro1/irods-test.txt')
        print myfile.get_size()

        print myfile.list_locations()

        mydir.make_dir("irods:///osg/home/azebro1/irods-test-dir/")

    except saga.Exception, ex:
        print "An error occured during file operation: %s" % (str(ex))
        sys.exit(-1)

    print "test script finished execution"

if __name__ == "__main__":
    main()
