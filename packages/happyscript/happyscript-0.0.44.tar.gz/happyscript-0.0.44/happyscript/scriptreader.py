#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________


import os, inspect, traceback
import wx
import importlib.util

class ScriptReader:
    ''' Imports scripts from a single directory.
    '''
    def __init__(self, script_dir, group_name = None):
        '''
            @param runner   Reference to the ScriptRunner that instantiated this reader
            @param script_dir  Directory to load the scripts from
        '''

        if group_name is None:                                  # if no name given, use directory name
            group_name = os.path.basename(script_dir)

        self.group_name = group_name
        self._script_dir = script_dir                   # directory containing script files
        self.func_help = dict()                              # help for each script function, key 'file.function'
        self.func_obj = dict()                              # script functions, key 'file.function'
        self.mdl = dict()                               # module used for loading each file, key 'file'
        self.func_names = dict()                         # list of function names per file, key 'file'

    def reload( self ):
        ''' Reloads all scripts of this directory.
        '''
        self.func_help.clear()
        self.func_obj.clear()
        self.mdl.clear()
        self.func_names.clear()

        print("Reading scripts from " + self._script_dir)

        files = os.listdir(self._script_dir)
         
        msg = ""
        for x in files:
            if not x.endswith(".py") or x=="__init__.py":
                continue
             
            print( "---> " + x )
            error = self.read_single_file(x)
            if error:
                msg = msg + "\n" + error
 
        if len(msg)>0:
            msg = "There were (more) errors :" + msg
            wx.MessageBox( msg, "Error importing files", wx.OK | wx.ICON_WARNING )
             
             
    def read_single_file(self, filename):
        ''' Import a python python file, and find all functions in it.
            A treeview item with the file name is created, and child nodes for each function.
            A reference is kept to all of the functions to call them later on.
        '''       
        fullfilename = os.path.join(self._script_dir, filename)
        try:            
            modname = os.path.splitext(filename)[0]                                 # import the module

            spec = importlib.util.spec_from_file_location(modname, fullfilename)
            mdl = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mdl)
                
            self.mdl[modname] = mdl
            self.func_names[modname] = list()
             
            for x in inspect.getmembers(mdl, inspect.isfunction):                   # we found a function    
                funcname = x[0]
                 
                doctxt = inspect.getdoc( x[1] )
                if not doctxt:                                                      # skip functions without comment    
                    continue
                 
                if not ("@public" in doctxt) and not ("\\public" in doctxt):       # only functions with 'public' tag
                    continue
 
                doctxt = doctxt.replace("@public","").replace("\\public","")

                if doctxt:                                                          # remember function help, if any
                    self.func_help["%s.%s" % (modname,funcname)] = doctxt            
                else:
                    self.func_help["%s.%s" % (modname,funcname)] = "No help"
                     
                self.func_obj["%s.%s" % (modname,funcname)] = x[1]                      # remember reference to function
                self.func_names[modname].append(funcname)                            # remember function name for this file    
                #print self.func_help["%s.%s" % (modname,funcname)]
        except:
            msg = traceback.format_exc()               
            wx.MessageBox( msg, "Error importing file %s" % (fullfilename), wx.OK | wx.ICON_WARNING )
             
        for fname in list(self.func_names.keys()):                               # delete all files without script functions
            if len(self.func_names[fname]) == 0:
                del self.func_names[fname]
             
        return None

    def get_file_list(self):
        ''' Get a list of all script files.
        '''
        if len(self.func_names)==0:
            return list()
        result = sorted(self.func_names.keys())
        return result
    
    def get_func_names(self, filename):
        ''' Get all the script functions in a script file.
            @param filename   Filename, as returned by get_file_list
        '''
        if not filename in self.func_names:
            return list()
        return sorted(self.func_names[filename])

    def get_help(self, filename, funcname):
        
        itemname = "%s.%s" % (filename, funcname)
        if itemname in self.func_help:
            return self.func_help[itemname]
        else:
            return "No help for %s.%s" % (filename, funcname)
        
    def get_func(self, filename, funcname):
        
        itemname = "%s.%s" % (filename, funcname)
        if itemname in self.func_obj:
            return self.func_obj[itemname]
        else:
            return None

