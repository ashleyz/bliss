#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

'''This examples removes a replica from a LFC entry.

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
        myrep = saga.logicalfile.LogicalFile('lfn://lfc.grid.sara.nl:5010/grid/vlemed/mark/bliss/input.txt') 
        sfn='srm://gb-se-ams.els.sara.nl/dpm/els.sara.nl/home/vlemed/vletgenerated/2012-05-31/input_txt_00a5d9a3-b4fa-4cb8-9d94-26531ad1ce64'

        myrep.add_location(sfn)

    except saga.Exception, ex:
        print "An error occured during file operation: %s" % (str(ex))
        sys.exit(-1)

if __name__ == "__main__":
    main()
