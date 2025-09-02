#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to manage script readout and execution
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import os

from .panels.panel_scripts2 import PanelScripts2
from .scriptreader import ScriptReader
from .staticscriptmanager import StaticScriptManager

class ScriptManager(StaticScriptManager):
    '''
    classdocs
    '''

    def __init__(self, title=None, colors = None, use_yaml=False):
        '''
            Constructor
            
            @param  Optional title for main window.
            @param  Optional color scheme for test list.
                    0=green, 1=blue, 2=yellow, 3=grey, 4=orange, 5=darker blue 
        '''
        super().__init__(title=title, colors=colors, use_yaml=use_yaml)          # call parent constructor

#============================================================================================================
#                    R E A D   S C R I P T S                       
#============================================================================================================

    def add_scripts(self, script_dir, group_name = None):
        ''' Reads scripts from a directory. 
            Then adds a script treeview window with the scripts from the specified directory.
            @param scriptDir   Full path to the directory with scripts
            @param group_name  Name for this set of scripts.  Dirname will be used if not specified. 
        '''
        full_path = os.path.normpath(os.path.abspath(script_dir))
        self.logger.info( "Adding scripts in %s" % full_path )

        if group_name is None:                                  # if no name given, use directory name
            group_name = os.path.basename(full_path)
        
        reader = ScriptReader(script_dir, group_name)           # create object to read scripts in this dir
        self._script_readers[group_name] = reader
        
        reader.reload()                                         # read the scripts
        
        newPanel = PanelScripts2(self.dialog._nbk_scripts, reader, self.ctrl ) # create script panel
        self.dialog._nbk_scripts.AddPage( newPanel, group_name, False)                   # add it in dialog
