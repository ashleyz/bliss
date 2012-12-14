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

        print "Printing directory listing"
        for entry in mydir.list():
            print entry

        print "Creating file object"
        myfile = saga.logicalfile.LogicalFile('irods:///osg/home/azebro1/irods-test.txt')
        
        print "size of test file"
        print myfile.get_size()

        print "locations the file is stored at:"
        print myfile.list_locations()

        print "Making test dir"
        mydir.make_dir("irods:///osg/home/azebro1/irods-test-dir/")

        print "Deleting test dir"
        mydir.remove("irods:///osg/home/azebro1/irods-test-dir/")

        print "Uploading file"
        myfile = saga.logicalfile.LogicalFile('irods:///osg/home/azebro1/testdir/PyRods-3.1.0.tar.gz')
        myfile.upload("/home/azebro1/PyRods-3.1.0.tar.gz", \
                     "irods:///this/path/is/ignored/?resource=Firefly")

        print "Deleting file"
        myfile.remove()

    except saga.Exception, ex:
        print "An error occured while executing the test script! %s" % (str(ex))
        sys.exit(-1)

    print "test script finished execution"

if __name__ == "__main__":
    main()
