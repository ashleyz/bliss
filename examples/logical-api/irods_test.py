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
import os

FILE_SIZE = 1 # in megs, approx
NUM_REPLICAS = 5 # num replicas to create
TEMP_FILENAME = "test.txt" # filename to create and use for testing
TEMP_DIR      = "/irods_test_dir/" #directory to create and use for testing
IRODS_DIRECTORY = "/osg/home/azebro1/" #directory to store our iRODS files in, don't forget trailing and leading /
IRODS_RESOURCE = "osgGridFtpGroup" #iRODS resource or resource group to upload files to

def main():
    # make sure we have a trailing / at the end of our iRODS directory name
    try:
        # grab our home directory (tested on Linux)
        home_dir = os.path.expanduser("~"+"/")
        print "Creating temporary file of size %dM : %s" % \
            (FILE_SIZE, home_dir+TEMP_FILENAME)

        # create a file for us to use with iRODS
        with open(home_dir+TEMP_FILENAME, "wb") as f:
            f.write ("x" * (FILE_SIZE * pow(2,20)) )

        print "Creating iRODS directory object"
        mydir = saga.logicalfile.LogicalDirectory("irods://" + IRODS_DIRECTORY) 

        print "Uploading file to iRODS"
        myfile = saga.logicalfile.LogicalFile('irods://'+IRODS_DIRECTORY+TEMP_FILENAME)
        myfile.upload(home_dir + TEMP_FILENAME, \
                     "irods:///this/path/is/ignored/?resource="+IRODS_RESOURCE)

        print "Deleting file locally : %s" % (home_dir + TEMP_FILENAME)
        os.remove(home_dir + TEMP_FILENAME)

        print "Printing iRODS directory listing for %s " % ("irods://" + IRODS_DIRECTORY)
        for entry in mydir.list():
            print entry

        print "Creating iRODS file object"
        myfile = saga.logicalfile.LogicalFile('irods://' + IRODS_DIRECTORY+TEMP_FILENAME)
        
        print "Size of test file %s on iRODS in bytes:" % (IRODS_DIRECTORY + TEMP_FILENAME)
        print myfile.get_size()

        print "Creating",NUM_REPLICAS,"replicas for",IRODS_DIRECTORY+TEMP_FILENAME
        for i in range(NUM_REPLICAS):
            myfile.replicate("irods:///this/path/is/ignored/?resource="+IRODS_RESOURCE)

        print "Locations the file is stored at on iRODS:"
        for entry in myfile.list_locations():
            print entry

        print "Downloading logical file %s to current/default directory" % \
            (IRODS_DIRECTORY + TEMP_FILENAME) 
        myfile.download()

        print "Downloading logical file %s to /tmp/" % \
            (IRODS_DIRECTORY + TEMP_FILENAME) 
        myfile.download("/tmp/")

        print "Deleting downloaded file locally : %s" % (os.getcwd() + TEMP_FILENAME)
        os.remove(os.getcwd() +"/" + TEMP_FILENAME)

        print "Deleting downloaded file locally : %s" % ("/tmp" + TEMP_FILENAME)
        os.remove("/tmp/" + TEMP_FILENAME)

        print "Making test dir %s on iRODS" % (IRODS_DIRECTORY+TEMP_DIR)
        mydir.make_dir("irods://"+IRODS_DIRECTORY+TEMP_DIR)
        
        #commented because iRODS install on gw68 doesn't support move
        #print "Moving file to %s test dir on iRODS" % (IRODS_DIRECTORY+TEMP_DIR)
        #myfile.move("irods://"+IRODS_DIRECTORY+TEMP_DIR)

        print "Deleting test dir %s from iRODS" % (IRODS_DIRECTORY+TEMP_DIR)
        mydir.remove("irods://"+IRODS_DIRECTORY+TEMP_DIR)

        print "Deleting file %s from iRODS" % (IRODS_DIRECTORY+TEMP_FILENAME)
        myfile.remove()

    except saga.Exception, ex:
        print "An error occured while executing the test script! %s" % (str(ex))
        sys.exit(-1)

    print "test script finished execution"

if __name__ == "__main__":
    main()
