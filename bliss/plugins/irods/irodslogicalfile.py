# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ashley Zebrowski"
__copyright__ = "Copyright 2012, Ashley Zebrowski"
__license__   = "MIT"

from bliss.interface import LogicalFilePluginInterface
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
        self.locations = ("undefined")
        self.size = 1234567899
        self.owner = "undefined"
        self.date = "1/1/1111"
        self.is_directory = False

def irods_get_listing(plugin, dir):
    result = []
    try:
        cw = CommandWrapper.initAsLocalWrapper(None)
        cw.connect()

        cw_result = cw.run("ils %s" % dir)

        print "running ils %s" % dir

        if cw_result.returncode != 0:
            raise Exception("Could not open directory")

        # strip extra linebreaks from stdout, make a list w/ linebreaks, skip first entry which tells us the current directory
        for item in cw_result.stdout.strip().split("\n"):
            item = item.strip()

            #entry for file or directory
            
            #we have a directory here
            if item.startswith("C- "):
                #result.append("dir " + item[3:])
                result.append(item[3:])

            #we have a file here
            else:
                #result.append("file " +item)
                result.append(item)

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
    _apis = ['saga.logicalfile']

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
        result = cw.run("which ils")
        if result.returncode != 0:
            print "Couldn't locate iRODS commandline tools: %s"  % (result.stdout)
        print result.returncode
        
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

        complete_url = str(file_obj._url)
        path = file_obj._url.get_path()
        listing = irods_get_listing(self, path)

        for i in listing:
            print i
        
        return 42
        
        return

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

        return


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
