# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ashley Zebrowski"
__copyright__ = "Copyright 2012, Ashley Zebrowski"
__license__   = "MIT"

from bliss.interface import LogicalFilePluginInterface
from bliss.interface import ResourcePluginInterface
from bliss.utils.command_wrapper import CommandWrapper, CommandWrapperException

import os, pwd
import sys
import time
import bliss.saga
import string
from bliss.saga.Error import Error as SAGAError
import errno
import logging

class irods_logical_entry():
    '''class to hold info on an iRODS logical file or directory
    '''
    def __init__(self):
        self.name = "undefined"
        self.locations = []
        self.size = 1234567899
        self.owner = "undefined"
        self.date = "1/1/1111"
        self.is_directory = False

    def __str__(self):
        return str(self.name + " " +  \
                   "/".join(self.locations) + " " + \
                   str(self.size) + " " + \
                   self.owner + " " + \
                   self.date + " " + \
                   str(self.is_directory))

class irods_resource_entry():
    '''class to hold info on an iRODS resource
    '''
    # Resources (not groups) as retreived from ilsresc -l look like the following:
    # resource name: BNL_ATLAS_2_FTP
    # resc id: 16214
    # zone: osg
    # type: MSS universal driver
    # class: compound
    # location: gw014k1.fnal.gov
    # vault: /data/cache/BNL_ATLAS_2_FTPplaceholder
    # free space:
    # status: up
    # info:
    # comment:
    # create time: 01343055975: 2012-07-23.09:06:15
    # modify time: 01347480717: 2012-09-12.14:11:57
    # ----

    # Resource groups look like this (shortened):
    
    # resource group: osgGridFtpGroup
    # Includes resource: NWICG_NotreDame_FTP
    # Includes resource: UCSDT2-B_FTP
    # Includes resource: UFlorida-SSERCA_FTP
    # Includes resource: cinvestav_FTP
    # Includes resource: SPRACE_FTP
    # Includes resource: NYSGRID_CORNELL_NYS1_FTP
    # Includes resource: Nebraska_FTP
    # -----

    def __init__(self):
        #are we a resource group? 
        self.is_resource_group = False

        #individual resource-specific properties
        self.name = "undefined"
        self.zone = "undefined"
        self.type = "undefined"
        self.resource_class = "undefined"
        self.location = "undefined"
        self.vault = "undefined"
        self.free_space = 123456789
        self.status = "undefined"
        self.info = "undefined"
        self.comment = "undefined"
        self.create_time = "undefined"
        self.modify_time = "undefined"

        #resource group-specific properties
        self.group_members = []

def irods_get_directory_listing(plugin, dir):
    '''function takes an iRODS logical directory as an argument,
       and returns a list of irods_logical_entry instances containing
       information on files/directories found in the directory argument
    '''

    result = []
    try:
        cw = CommandWrapper.initAsLocalWrapper(None)
        cw.connect()
        
        # execute the ils -L command
        cw_result = cw.run("ils -L %s" % dir)

        # make sure we ran ok
        if cw_result.returncode != 0:
            raise Exception("Could not open directory %s, errorcode %s: %s"\
                                    % (dir, str(cw_result.returncode),
                                       cw_result))

        # strip extra linebreaks from stdout, make a list from the linebreaks that
        # remain, skip first entry which just tells us the current directory
        for item in cw_result.stdout.strip().split("\n"):

            # if we are listing a directory or remote resource file location i.e.
            # (bliss-irods)[azebro1@gw68 bliss]$ ils -L /osg/home/azebro1
            # /osg/home/azebro1:
            #    azebro1           1 UFlorida-SSERCA_FTP            12 2012-11-14.09:55 & irods-test.txt
            #          /data/cache/UFlorida-SSERCA_FTPplaceholder/home/azebro1/irods-test.txt    osgGridFtpGroup

            # then we want to ignore that entry (not using it for now)
            if item.strip().startswith("/"):
                continue 
            
            #remove whitespace
            item = item.strip()

            #entry for file or directory
            dir_entry = irods_logical_entry()
            
            #if we have a directory here
            if item.startswith("C- "):
                dir_entry.name = item[3:]
                dir_entry.is_directory = True

            #if we have a file here
            else:
                # ils -L output looks like this after you split it:
                #  0           1    2                      3     4                   5    6
                # ['azebro1', '1', 'UFlorida-SSERCA_FTP', '12', '2012-11-14.09:55', '&', 'irods-test.txt']
                # not sure what 1 and 5 are ... 
                dir_entry.owner = item.split()[0]
                dir_entry.locations = [item.split()[2]]
                dir_entry.size = item.split()[3]
                dir_entry.date = item.split()[4]
                dir_entry.name = item.split()[6]

            result.append(dir_entry)

        # merge all entries on the list with duplicate filenames into a
        # single entry with one filename and multiple resource locations
        final_list = []
        for item in result:
            if item.name in [i.name for i in final_list]:
                #duplicate name, merge this entry with the previous one
                for final_list_item in final_list:
                    if final_list_item.name == item.name:
                        final_list_item.locations.append(item.locations[0])
            else:
                final_list.append(item)
        return final_list

    except Exception, e:
        plugin.log_error_and_raise(bliss.saga.Error.NoSuccess, "Couldn't get directory listing: %s " % (str(e)))

    return result

def irods_get_resource_listing(plugin):
    ''' Return a list of irods resources and resource groups with information
        stored in irods_resource_entry format
    '''
    result = []
    try:
        cw = CommandWrapper.initAsLocalWrapper(None)
        cw.connect()

        # execute the ilsresc -l command
        cw_result = cw.run("ilsresc -l")

        # make sure we ran ok
        if cw_result.returncode != 0:
            raise Exception("Could not obtain list of resources with ilsresc -l")

        # convert our command's stdout to a list of text lines
        cw_result_list = cw_result.stdout.strip().split("\n")

        # list of resource entries we will save our results to
        result = []

        # while loop instead of for loop so we can mutate the list
        # as we iterate
        while cw_result_list:
            entry = irods_resource_entry()
            
            # get our next line from the FRONT of the list
            line = cw_result_list.pop(0)
            
            # check to see if this is the beginning of a
            # singular resource entry 
            if line.startswith("resource name: "):
                # singular resource entry output from ilsresc -l
                # LINE NUMBERS AND PADDING ADDED
                # ex. actual output, line 0 starts like "resource name"
                # 0  resource name: BNL_ATLAS_2_FTP
                # 1  resc id: 16214
                # 2  zone: osg
                # 3  type: MSS universal driver
                # 4  class: compound
                # 5  location: gw014k1.fnal.gov
                # 6  vault: /data/cache/BNL_ATLAS_2_FTPplaceholder
                # 7  free space:
                # 8  status: up
                # 9  info:
                # 10 comment:
                # 11 create time: 01343055975: 2012-07-23.09:06:15
                # 12 modify time: 01347480717: 2012-09-12.14:11:57
                # 13 ----
                entry.name = line[len("resource name: "):].strip()
                entry.is_resource_group = False

                # TODO: SAVE ALL THE OTHER INFO
                for i in range(13):
                    cw_result_list.pop(0)

                #add our resource to the list
                result.append(entry)

            # check to see if this is an entry for a resource group
            elif line.startswith("resource group: "):
                entry.name = line[len("resource group: "):].strip()
                entry.is_resource_group = True

                # continue processing ilsresc -l results until we
                # are at the end of the resource group information
                # ----- is not printed if there are no further entries
                # so we have to make sure to check we don't pop off an empty
                # stack too
                #
                # TODO: ACTUALLY SAVE THE LIST OF RESOURCES IN A RESOURCE GROUP
                while len(cw_result_list)>0 and (not line.startswith("-----")):
                    line=cw_result_list.pop(0)

                result.append(entry)

            # for some reason, we're at a line which we have no idea how to handle
            # this is bad -- throw an error
            else:
                plugin.log_error(bliss.saga.Error.NoSuccess, "Error parsing iRODS"+\
                                     " ilsresc -l information!")
                raise ("ilsresc -l parsing error")
                
        return result

    except Exception, e:
        plugin.log_error_and_raise(bliss.saga.Error.NoSuccess, "Couldn't get resource listing: %s " % (str(e)))


################################################################################
class iRODSLogicalFilePlugin(LogicalFilePluginInterface):
    '''Implements a logicalfile plugin that does things via lfc2
    '''
    #
    ## Define adaptor name. Convention is:
    ##         saga.plugin.<package>.<name>
    _name = 'saga.plugin.logicalfile.irods'

    ## Define supported url schemas
    ## 
    _schemas = ['irods']

    ## Define apis supported by this adaptor
    ##
    _apis = ['saga.logicalfile', 'saga.resource']

    ##
    def __init__(self, url):
        '''Class constructor'''
        LogicalFilePluginInterface.__init__(self, name=self._name, schemas=self._schemas)
        
        # store a commandwrapper to run our iRODS commands through
        cw = CommandWrapper.initAsLocalWrapper(logger=self)
        cw.connect()
        self._cw = cw
     
    @classmethod
    def sanity_check(self):
        '''Implements interface from PluginBaseInterface
        '''
        cw = CommandWrapper.initAsLocalWrapper(logger=self)
        cw.connect()

        # run ils, see if we get any errors -- if so, fail the
        # sanity check
        try:
            result = cw.run("ils")
            if result.returncode != 0:
                raise Exception("sanity check error")
        except Exception, ex:
            raise Exception("Disabling iRODS plugin - could not access iRODS "+\
                            "filesystem through ils.  Check your iRODS "+\
                            "environment and certificates.")
        # try ienv or imiscsvrinfo later? ( check for error messages )
        return
            
    ######################################################################
    ##  
    def register_logicalfile_object(self, file_obj):
        '''Implements interface from FilesystemPluginInterface
        '''     
        pass

        # TODO: "stat" the file

    ######################################################################
    ## 
    def unregister_logicalfile_object(self, service_obj):
        '''Implements interface from FilesystemPluginInterface
        '''
        pass

    ######################################################################
    ##  
    def register_logicaldirectory_object(self, file_obj):
        '''Implements interface from FilesystemPluginInterface
        '''     
        pass

    ######################################################################
    ##
    def unregister_logicaldirectory_object(self, dir_obj):
        '''Implements interface from FilesystemPluginInterface
        '''
        pass

    ######################################################################
    ##
    def dir_list(self, dir_obj, pattern):
        #TODO: Make this use the irods_get_directory_listing

        complete_path = dir_obj._url.path
        result = []

        self.log_debug("Attempting to get directory listing for logical path %s" % complete_path)

        try:
            cw_result = self._cw.run("ils %s" % complete_path)
            
            if cw_result.returncode != 0:
                raise Exception("Could not open directory")

            # strip extra linebreaks from stdout, make a list w/ linebreaks, skip first entry which tells us the current directory
            for item in cw_result.stdout.strip().split("\n")[1:]:
                item = item.strip()
                if item.startswith("C- "):
                    #result.append("dir " + item[3:])
                    result.append(item[3:])
                else:
                    #result.append("file " +item)
                    result.append(item)

        except Exception, ex:
            self.log_error_and_raise(bliss.saga.Error.NoSuccess, "Couldn't list directory: %s " % (str(ex)))

        return result

    ######################################################################
    ## 

    def file_get_size(self, file_obj):
        '''Implements interface from FilesystemPluginInterface
        '''
        path = file_obj._url.get_path()
        self.log_debug("Attempting to get size for logical file %s " \
                           path)
        listing = irods_get_directory_listing(self, path)
        return listing[0].size

    ######################################################################
    ##
    def dir_make_dir(self, dir_obj, path, flags):
        '''Implements interface from FilesystemPluginInterface
        '''
        #complete_path = dir_obj._url.path
        complete_path = bliss.saga.Url(path).get_path()
        self.log_debug("Attempting to make directory at: %s" % complete_path)

        #attempt to run iRODS mkdir command
        try:
            cw_result = self._cw.run("imkdir %s" % complete_path)

            if cw_result.returncode != 0:
                raise Exception("Could not create directory %s, errorcode %s: %s"\
                                    % (complete_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            # did the directory already exist?
            if "CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME" in str(ex):
                self.log_error_and_raise(bliss.saga.Error.AlreadyExists,
                                         "Directory already exists.")
            # couldn't create for unspecificed reason
            self.log_error_and_raise(bliss.saga.Error.NoSuccess, 
                                     "Couldn't create directory.")
        return

    ######################################################################
    ##
    def dir_remove(self, dir_obj, path=None):
        '''This method is called upon logicaldir.remove()
        '''
        complete_path = bliss.saga.Url(path).get_path()
        self.log_debug("Attempting to remove directory at: %s" % complete_path)

        try:
            cw_result = self._cw.run("irm -r %s" % complete_path)

            if cw_result.returncode != 0:
                raise Exception("Could not remove directory %s, errorcode %s: %s"\
                                    % (complete_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            # was there no directory to delete?
            if "does not exist" in str(ex):
                self.log_error_and_raise(bliss.saga.Error.DoesNotExist,
                                         "Directory %s does not exist."\
                                         % (complete_path) )

            # couldn't delete for unspecificed reason
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't delete directory %s"\
                                     % (complete_path))
        return

    ######################################################################
    ##
    def logicalfile_list_locations(self, logicalfile_obj):
        '''This method is called upon logicaldir.list_locations()
        '''
        #return a list of all replica locations for a file
        path = logicalfile_obj._url.get_path()
        self.log_debug("Attempting to get a list of replica locations for %s" \
                           % path)
        listing = irods_get_directory_listing(self, path)
        return listing[0].locations

    ######################################################################
    ##
    def logicalfile_remove_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.remove_locations()
        '''     
        self.log_error_and_raise(SAGAError.NotImplemented, "Not implemented")
        return

    ######################################################################
    ##
    def logicalfile_replicate(self, logicalfile_obj, target):
        '''This method is called upon logicaldir.replicate()
        '''        
        #path to file we are replicating on iRODS
        complete_path = logicalfile_obj._url.get_path()        

        #TODO: Verify Correctness in the way the resource is grabbed
        query = bliss.saga.Url(target).get_query()
        resource = query.split("=")[1]
        self.log_debug("Attempting to replicate logical file %s to resource/resource group %s" % (complete_path, resource))

        try:
            cw_result = self._cw.run("irepl -R %s %s" % (resource, complete_path) )

            if cw_result.returncode != 0:
                raise Exception("Could not replicate logical file %s to resource/resource group %s, errorcode %s: %s"\
                                    % (complete_path, resource, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't replicate file.")
        return

    ######################################################################
    ##
    # TODO: This is COMPLETELY untested, as it is unsupported on the only iRODS
    # machine I have access to.
    def file_move(self, logicalfile_obj, target):
        '''This method is called upon logicaldir.move()
        '''
        #path to file we are moving on iRODS
        source_path = logicalfile_obj._url.get_path()
        dest_path   = bliss.saga.Url(target).get_path()

        self.log_debug("Attempting to move logical file %s to location %s" % (source_path, dest_path))

        try:
            cw_result = self._cw.run("imv %s %s" % (source_path, dest_path) )

            if cw_result.returncode != 0:
                raise Exception("Could not move logical file %s to location %s, errorcode %s: %s"\
                                    % (source_path, dest_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't move file.")
        return



    ######################################################################
    ##
    def logicalfile_add_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.add_location()
        '''
        self.log_error_and_raise(SAGAError.NotImplemented, "Not implemented")
        return

    ######################################################################
    ##
    def file_remove(self, logicalfile_obj):
        '''This method is called upon logicalfile.remove()
        '''
        complete_path = logicalfile_obj._url.get_path()
        self.log_debug("Attempting to remove file at: %s" % complete_path)

        try:
            cw_result = self._cw.run("irm %s" % complete_path)

            if cw_result.returncode != 0:
                raise Exception("Could not remove file %s, errorcode %s: %s"\
                                    % (complete_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            # couldn't delete for unspecificed reason
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't delete file %s"\
                                     % (complete_path))
        return

    ######################################################################
    ##   
    #
    # From a convo with Andre M...
    #
    # So, if you want to have a logical file in that logical dir, you would create it:
    # myfile = mydir.open (irods.tar.gz, saga.replica.Create |
    #                      saga.replica.ReadWrite)
    # and then upload
    # myfile.upload ("file://home/ashley/my/local/filesystem/irods.tar.gz")
    # OR (revised)
    # myfile.upload("file://home/ashley/my/local/filesystem/irods.tar.gz",
    #               "irods://.../?resource=host3")
    # 
    # THIS IS A FUNCTION FOR A **PROPOSED** PART OF THE SAGA API!!!
    # HERE BE DRAGONS, in other words...

    def file_upload(self, logicalfile_obj, source, target=None):
        '''Uploads a file from the LOCAL, PHYSICAL filesystem to
           the replica management system.
           @param source: URL (should be file:// or local path) of local file
           @param target: Optional param containing ?resource=myresource query
                          This will upload the file to a specified iRODS
                          resource or group.
        '''

        #TODO: Make sure that the source URL is a local/file:// URL
        complete_path = bliss.saga.Url(source).get_path()
        
        # extract the path from the LogicalFile object, excluding
        # the filename
        destination_path=logicalfile_obj._url.get_path()[0:string.rfind(
                         logicalfile_obj._url.get_path(), "/")+1]

        try:
            #var to hold our command result, placed here to keep in scope
            cw_result = 0
            
            #mark that this is experimental/may not be part of official API
            self.log_debug("Beginning EXPERIMENTAL upload operation " +\
                           "will register file in logical dir: %s" %
                           destination_path)

            # was no resource selected?
            if target==None:
                self.log_debug("Attempting to upload to default resource")
                cw_result = self._cw.run("iput %s %s" %
                                         (complete_path, destination_path))

            # resource was selected, have to parse it and supply to iput -R
            else:
                #TODO: Verify correctness
                query = bliss.saga.Url(target).get_query()
                resource = query.split("=")[1]
                self.log_debug("Attempting to upload to resource %s" % resource)
                cw_result = self._cw.run("iput -R %s %s %s" %
                                         (resource, complete_path, destination_path))

            # check our result
            if cw_result.returncode != 0:
                raise Exception("Could not upload file %s, errorcode %s: %s"\
                                    % (complete_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            # couldn't upload for unspecificed reason
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't upload file.")
        return

    ######################################################################
    ##   
    # THIS IS A FUNCTION FOR A **PROPOSED** PART OF THE SAGA API!!!
    # HERE BE DRAGONS, in other words...

    def file_download(self, logicalfile_obj, target=None):
        '''Downloads a file from the REMOTE REPLICA FILESYSTEM to a local
           directory.
           @param target: Optional param containing a local path/filename
                          to save the file to
        '''

        #TODO: Make sure that the target URL is a local/file:// URL
        # extract the path from the LogicalFile object, excluding
        # the filename
        logical_path=logicalfile_obj._url.get_path()

        # fill in our local path if one was specified
        local_path = ""
        if target:
            local_path = bliss.saga.Url(target).get_path()
        
        try:
            #var to hold our command result, placed here to keep in scope
            cw_result = 0
            
            #mark that this is experimental/may not be part of official API
            self.log_debug("Beginning EXPERIMENTAL download operation " +\
                           "will download logical file: %s, specified local directory is %s" %
                           (logical_path, target) )

            # was no local target selected?
            if target==None:
                self.log_debug("Attempting to download file %s with iget to current local directory" % \
                                   logical_path)
                cw_result = self._cw.run("iget %s" % \
                                         (logical_path))

            # local target selected
            else:
                self.log_debug("Attempting to download file %s with iget to %s" % (logical_path, local_path))
                cw_result = self._cw.run("iget %s %s " %
                                         (logical_path, local_path))

            # check our result
            if cw_result.returncode != 0:
                raise Exception("Could not download file %s, errorcode %s: %s"\
                                    % (logical_path, str(cw_result.returncode),
                                       cw_result))

        except Exception, ex:
            # couldn't download for unspecificed reason
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                                     "Couldn't download file.")
        return
