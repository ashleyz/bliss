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
from bliss.saga.Error import Error as SAGAError
import errno
import logging

#class to hold info on a file or directory
class irods_entry():
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

def irods_get_listing(plugin, dir):
    result = []
    try:
        cw = CommandWrapper.initAsLocalWrapper(None)
        cw.connect()
        
        # execute the ils -L command
        cw_result = cw.run("ils -L %s" % dir)

        # make sure we ran ok
        if cw_result.returncode != 0:
            raise Exception("Could not open directory")

        # strip extra linebreaks from stdout, make a list w/ linebreaks, skip first entry which tells us the current directory
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
            dir_entry = irods_entry()
            
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

        # TODO: merge all entries on the list with duplicate filenames into a
        #       single entry, and use the locations attribute
        #       to keep track of where they're saved

        final_list = []
        for item in result:
            if item.name in [i.name for i in final_list]:
                #duplicate name, merge this entry with the previous one
                for final_list_item in final_list:
                    if final_list_item.name == item.name:
                        final_list_item.locations.append(item.locations[0])
            else:
                final_list.append(item)

        unique_name = list(set([i.name for i in final_list]))
        return final_list

    except Exception, e:
        plugin.log_error_and_raise(bliss.saga.Error.NoSuccess, "Couldn't get directory listing: %s " % (str(e)))

    return result


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
        
        cw = CommandWrapper.initAsLocalWrapper(logger=self)
        cw.connect()
        self._cw = cw
     
    @classmethod
    def sanity_check(self):
        '''Implements interface from PluginBaseInterface
        '''
        cw = CommandWrapper.initAsLocalWrapper(logger=self)
        cw.connect()

        # run ils, see if we get any errors -- if so, 
        try:
            result = cw.run("ils")
            if result.returncode != 0:
                #print "Error running ils to check for a working iRODS environment "+\
                #    "- check your iRODS configuration and certificates. "+\
                #    "%s"  % (result.stdout)
                raise Exception("Cats")
        except Exception, ex:
            raise Exception("Disabling iRODS plugin - could not access iRODS "+\
                            "filesystem through ils.  Check your iRODS "+\
                            "environment and certificates.")
        # try ienv or imiscsvrinfo later? ( check for error messages )

        return
        #try:
        #    import lfc2
        #except Exception, ex:
        #    raise Exception("lfc2 module missing")
            
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

        complete_path = dir_obj._url.path
        result = []

        self.log_debug("Attempting to get listing for %s" % complete_path)

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

        # try:
        #     self.log_info("Trying to LSDIR '%s'" % (complete_path))

        #     dir = lfc.lfc_opendir(complete_path)
        #     if dir == None:
        #         raise Exception('Could not open dir')

        #     while True:
        #         entry = lfc.lfc_readdirxr(dir)
        #         if entry == None:
        #             break
        #         result.append(entry.d_name)

        #     lfc.lfc_closedir(dir)

        # except Exception, ex:
        #     self.log_error_and_raise(bliss.saga.Error.NoSuccess,
        #     "Couldn't list directory: %s " % (str(ex)))

        return result


    ######################################################################
    ## 

    def file_get_size(self, file_obj):
        '''Implements interface from FilesystemPluginInterface
        '''
        path = file_obj._url.get_path()
        listing = irods_get_listing(self, path)
        return listing[0].size

        # complete_url = str(file_obj._url)
        # try:
        #     return lcg_get_size(complete_url)
        # except Exception, ex:
        #     self.log_error_and_raise(bliss.saga.Error.NoSuccess, 
        #     "Couldn't determine size for '%s': %s " % (complete_url, (str(ex))))


    ######################################################################
    ##
    def logicaldir_make_dir(self, dir_obj, path, flags):
        '''Implements interface from FilesystemPluginInterface
        '''
        return

        # complete_path = os.path.join(dir_obj._url.path, path)
        # complete_url = str(dir_obj._url) + '/' + path

        # # LOCAL FILESYSTEM
        # if dir_obj.is_local:
        #     if os.path.exists(complete_path):
        #         self.log_error_and_raise(bliss.saga.Error.AlreadyExists,
        #          "Couldn't create directory '%s'. Entry already exist." % (complete_path))
        #     else:
        #         os.mkdir(complete_path)

        # # REMOTE FILESYSTEM VIA GFAL
        # else:
        #     # throw exception if directory already exists
        #     #stat = self.entry_getstat(dir_obj, path)
        #     #if stat != None:
        #     #    self.log_error_and_raise(bliss.saga.Error.AlreadyExists,
        #     #     "Couldn't create directory '%s'. Entry already exist." % (complete_path))

        #     try:
        #         self.log_debug('Creating directory: ' + complete_url)
        #         lcg_mkdir(complete_url, 0640, 'vlemed')

        #     except Exception, ex:
        #         self.log_error_and_raise(bliss.saga.Error.NoSuccess,
        #          "Couldn't create directory '%s': %s " % (complete_path, str(ex)))


    ######################################################################
    ##
    def logicaldir_remove(self, dir_obj, path=None):
        '''This method is called upon logicaldir.remove()
        '''

        return

        # if path != None:
        #     complete_path = os.path.join(dir_obj._url.path, path)
        #     complete_url = str(dir_obj._url) + '/' + path
        # else:
        #     complete_path = dir_obj._url.path
        #     complete_url = str(dir_obj._url)

        # # LOCAL FILESYSTEM
        # if dir_obj.is_local:
        #     from shutil import rmtree
        #     return rmtree(complete_path)

        # # REMOTE FILESYSTEM VIA GFAL
        # else:
        #     try:
        #         self.log_info("Trying to (recursively) RMDIR '%s'" % (complete_url))
        #         # TODO: recursive

        #         lcg_rmdir(complete_url)

        #     except Exception, ex:
        #         self.log_error_and_raise(bliss.saga.Error.NoSuccess,
        #          "Couldn't remove directory '%s': %s " % (complete_url, str(ex)))

    

    ######################################################################
    ##
    def logicalfile_list_locations(self, logicalfile_obj):
        '''This method is called upon logicaldir.list_locations()
        '''

        #return a list of all locations the file is located at

        path = logicalfile_obj._url.get_path()
        listing = irods_get_listing(self, path)
        return listing[0].locations


        # complete_path = logicalfile_obj._url.path
        # result = []

        # try:
        #     list = lfc.lfc_getreplica(complete_path, None, None)

        #     for i in list:
        #         #print i.host, i.sfn, i.status, i.fs, i.poolname, \
        #         #      i.fileid, i.nbaccesses, i.f_type
        #         result.append(i.sfn)

        # except Exception, ex:
        #     print ex
        
        # return result

    ######################################################################
    ##
    def logicalfile_remove_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.remove_locations()
        '''

        return

        # complete_path = str(logicalfile_obj._url.path)

        # try:
        #     stat = lfc.lfc_statg(complete_path, '')
        #     guid = stat.guid
        # except Exception, ex:
        #     print 'Error during lfc_statg:', ex

        # try:
        #     lfc.lfc_delreplica(guid, None, location)
        # except ValueError:
        #     print 'Value Error during lfc_delreplica: (replica not existing?)'
        # except SyntaxError:
        #     print 'SyntexError during lfc_delreplica (wrong guid?)'
        # except UnboundLocalError:
        #     print 'UnboundLocalError during lfc_delreplica: (wrong lfn?)'
        # except Exception:
        #     print 'Unknown Error during lfc_delreplica:', sys.exc_info()[0]


    ######################################################################
    ##
    def logicalfile_add_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.add_location()
        '''

        return

        # lfn = str(logicalfile_obj._url.path)

        # try:
        #     stat = lfc.lfc_statg(lfn, '')
        #     guid = stat.guid
        # except Exception, ex:
        #     print 'Error during lfc_statg:', ex

        # se = location
        # sfn = None
        # try:
        #     lfc.lfc_addreplica(guid, None, 'srm.grid.sara.nl', se, '-', 'D', '', '')
        # except ValueError:
        #     print 'Value Error during lfc_addreplica (replica already existing)'
        # except SyntaxError:
        #     print 'SyntexError during lfc_addreplica'
        # except UnboundLocalError:
        #     print 'UnboundLocalError during lfc_addreplica'
        # except Exception:
        #    print 'Unknown Error during lfc_addreplica:', sys.exc_info()[0]
