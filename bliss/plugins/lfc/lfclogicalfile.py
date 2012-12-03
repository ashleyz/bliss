# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2012, Mark Santcroos"
__license__   = "MIT"

from bliss.interface import LogicalFilePluginInterface

import os, pwd
import sys
import time
import bliss.saga
from bliss.saga.Error import Error as SAGAError
import errno

import logging

import lfc2 as lfc

################################################################################

class LFCLogicalFilePlugin(LogicalFilePluginInterface):
    '''Implements a logicalfile plugin that does things via lfc2
    '''
    ## Define adaptor name. Convention is:
    ##         saga.plugin.<package>.<name>
    _name = 'saga.plugin.logicalfile.lfc'

    ## Define supported url schemas
    ## 
    _schemas = ['lfn']

    ## Define apis supported by this adaptor
    ##
    _apis = ['saga.logicalfile']

    ##
    def __init__(self, url):
        '''Class constructor'''
        LogicalFilePluginInterface.__init__(self, name=self._name, schemas=self._schemas)

    @classmethod
    def sanity_check(self):
        '''Implements interface from PluginBaseInterface
        '''
        try:
            import lfc2
        except Exception, ex:
            raise Exception("lfc2 module missing")
            
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

        try:
            self.log_info("Trying to LSDIR '%s'" % (complete_path))

            dir = lfc.lfc_opendir(complete_path)
            if dir == None:
                raise Exception('Could not open dir')

            while True:
                entry = lfc.lfc_readdirxr(dir)
                if entry == None:
                    break
                result.append(entry.d_name)

            lfc.lfc_closedir(dir)

        except Exception, ex:
            self.log_error_and_raise(bliss.saga.Error.NoSuccess,
            "Couldn't list directory: %s " % (str(ex)))

        return result


    ######################################################################
    ## 
    def file_get_size(self, file_obj):
        '''Implements interface from FilesystemPluginInterface
        '''

        complete_url = str(file_obj._url)
        try:
            return lcg_get_size(complete_url)
        except Exception, ex:
            self.log_error_and_raise(bliss.saga.Error.NoSuccess, 
            "Couldn't determine size for '%s': %s " % (complete_url, (str(ex))))


    ######################################################################
    ##
    def logicaldir_make_dir(self, dir_obj, path, flags):
        '''Implements interface from FilesystemPluginInterface
        '''
        complete_path = os.path.join(dir_obj._url.path, path)
        complete_url = str(dir_obj._url) + '/' + path

        # LOCAL FILESYSTEM
        if dir_obj.is_local:
            if os.path.exists(complete_path):
                self.log_error_and_raise(bliss.saga.Error.AlreadyExists,
                 "Couldn't create directory '%s'. Entry already exist." % (complete_path))
            else:
                os.mkdir(complete_path)

        # REMOTE FILESYSTEM VIA GFAL
        else:
            # throw exception if directory already exists
            #stat = self.entry_getstat(dir_obj, path)
            #if stat != None:
            #    self.log_error_and_raise(bliss.saga.Error.AlreadyExists,
            #     "Couldn't create directory '%s'. Entry already exist." % (complete_path))

            try:
                self.log_debug('Creating directory: ' + complete_url)
                lcg_mkdir(complete_url, 0640, 'vlemed')

            except Exception, ex:
                self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                 "Couldn't create directory '%s': %s " % (complete_path, str(ex)))


    ######################################################################
    ##
    def logicaldir_remove(self, dir_obj, path=None):
        '''This method is called upon logicaldir.remove()
        '''
        if path != None:
            complete_path = os.path.join(dir_obj._url.path, path)
            complete_url = str(dir_obj._url) + '/' + path
        else:
            complete_path = dir_obj._url.path
            complete_url = str(dir_obj._url)

        # LOCAL FILESYSTEM
        if dir_obj.is_local:
            from shutil import rmtree
            return rmtree(complete_path)

        # REMOTE FILESYSTEM VIA GFAL
        else:
            try:
                self.log_info("Trying to (recursively) RMDIR '%s'" % (complete_url))
                # TODO: recursive

                lcg_rmdir(complete_url)

            except Exception, ex:
                self.log_error_and_raise(bliss.saga.Error.NoSuccess,
                 "Couldn't remove directory '%s': %s " % (complete_url, str(ex)))

    

    ######################################################################
    ##
    def logicalfile_list_locations(self, logicalfile_obj):
        '''This method is called upon logicaldir.list_locations()
        '''

        complete_path = logicalfile_obj._url.path
        result = []

        try:
            list = lfc.lfc_getreplica(complete_path, None, None)

            for i in list:
                #print i.host, i.sfn, i.status, i.fs, i.poolname, \
                #      i.fileid, i.nbaccesses, i.f_type
                result.append(i.sfn)

        except Exception, ex:
            print ex
        
        return result

    ######################################################################
    ##
    def logicalfile_remove_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.remove_locations()
        '''

        complete_path = str(logicalfile_obj._url.path)

        try:
            stat = lfc.lfc_statg(complete_path, '')
            guid = stat.guid
        except Exception, ex:
            print 'Error during lfc_statg:', ex

        try:
            lfc.lfc_delreplica(guid, None, location)
        except ValueError:
            print 'Value Error during lfc_delreplica: (replica not existing?)'
        except SyntaxError:
            print 'SyntexError during lfc_delreplica (wrong guid?)'
        except UnboundLocalError:
            print 'UnboundLocalError during lfc_delreplica: (wrong lfn?)'
        except Exception:
            print 'Unknown Error during lfc_delreplica:', sys.exc_info()[0]


    ######################################################################
    ##
    def logicalfile_add_location(self, logicalfile_obj, location):
        '''This method is called upon logicaldir.add_location()
        '''

        lfn = str(logicalfile_obj._url.path)

        try:
            stat = lfc.lfc_statg(lfn, '')
            guid = stat.guid
        except Exception, ex:
            print 'Error during lfc_statg:', ex

        se = location
        sfn = None
        try:
            lfc.lfc_addreplica(guid, None, 'srm.grid.sara.nl', se, '-', 'D', '', '')
        except ValueError:
            print 'Value Error during lfc_addreplica (replica already existing)'
        except SyntaxError:
            print 'SyntexError during lfc_addreplica'
        except UnboundLocalError:
            print 'UnboundLocalError during lfc_addreplica'
        except Exception:
            print 'Unknown Error during lfc_addreplica:', sys.exc_info()[0]
