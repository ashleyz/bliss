# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Mark Santcroos"
__copyright__ = "Copyright 2012, Mark Santcroos"
__license__   = "MIT"

from bliss.interface import PluginBaseInterface

from bliss.saga.Error import Error as SAGAError
from bliss.saga.Exception import Exception as SAGAException

class LogicalFilePluginInterface(PluginBaseInterface):
    '''Abstract base class for all logical filesystem plugins'''
 
    def __init__(self, name, schemas):
        '''Class constructor'''
        PluginBaseInterface.__init__(self, name=name, schemas=schemas,
                                     api=PluginBaseInterface.api_type_saga_logicalfile)
    
    def register_logicalfile_object(self, logicalfile_obj):
        '''This method is called upon instantiation of a new logicalfile object
        '''
        errormsg = "Not implemented plugin method called: register_logicalfile_object()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg) 

    def unregister_logicalfile_object(self, logicalfile_obj):
        '''This method is called upon deletion of a logicalfile object
        '''
        self.log_error("Not implemented plugin method called: unregister_logicalfile_object()")
        # don't throw -- destructor context

    def register_logicaldirectory_object(self, logicaldir_obj):
        '''This method is called upon instantiation of a new logicaldirectory object
        '''
        errormsg = "Not implemented plugin method called: register_logicaldirectory_object()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg) 

    def unregister_logicaldirectory_object(self, logicaldir_obj):
        '''This method is called upon deletion of a logicaldirectory object
        '''
        self.log_error("Not implemented plugin method called: unregister_logicaldirectory_object()")
        # don't throw -- destructor context

    def logicalfile_add_location(self, logicalfile_obj, location):
        '''This method is called upon logicalfile.add_location()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_add_location()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicalfile_remove_location(self, logicalfile_obj, location):
        '''This method is called upon logicalfile.remove_location()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_remove_location()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicalfile_update_location(self, logicalfile_obj, location_old, location_new):
        '''This method is called upon logicalfile.update_location()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_update_location()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicalfile_list_locations(self, logicalfile_obj):
        '''This method is called upon logicalfile.list_locations()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_list_locations()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicalfile_replicate(self, logicalfile_obj, target):
        '''This method is called upon logicalfile.replicate()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_replicate()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicalfile_remove(self, logicalfile_obj):
        '''This method is called upon logicalfile.remove()
        '''
        errormsg = "Not implemented plugin method called: logicalfile_remove()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicaldir_close(self, logicaldir_obj):
        '''This method is called upon logicaldir.close()
        ''' 
        errormsg = "Not implemented plugin method called: logicaldir_close()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicaldir_list(self, logicaldir_obj, pattern):
        '''This method is called upon logicaldir.list()
        '''
        errormsg = "Not implemented plugin method called: logicaldir_list()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicaldir_remove(self, logicaldir_obj, path=None):
        '''This method is called upon logicaldir.remove()
        '''
        errormsg = "Not implemented plugin method called: logicaldir_remove()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicaldir_make_dir(self, logicaldir_obj, path, flags):
        '''This methid is called upon logicaldir.make_dir()
        ''' 
        errormsg = "Not implemented plugin method called: logicaldir_make_dir()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def logicaldir_move(self, logicaldir_obj, path):
        '''This methid is called upon logicaldir.move()
        ''' 
        errormsg = "Not implemented plugin method called: logicaldir_make_dir()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def upload(self, source, target):
        '''This method is called upon logicalfile.upload()
        ''' 
        errormsg = "Not implemented plugin method called: logicalfile_upload()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)

    def download(self, target):
        '''This method is called upon logicalfile.download()
        ''' 
        errormsg = "Not implemented plugin method called: logicalfile_download()"
        self.log_error_and_raise(SAGAError.NotImplemented, errormsg)
