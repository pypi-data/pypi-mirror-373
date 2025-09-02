#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Read script functions from a module
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : n/a
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 10/7/2025
#__________________________________________________|_________________________________________________________


import inspect, traceback
import wx

class ModuleReader:
    ''' Imports scripts from a single directory.
    '''
    def __init__(self, module, group_name):
        '''
            @param runner   Reference to the ScriptRunner that instantiated this reader
            @param script_dir  Directory to load the scripts from
        '''

        self.module = module
        self.group_name = group_name
        self._script_dir = ""                   # directory containing script files
        self.func_help = dict()                              # help for each script function, key 'file.function'
        self.func_obj = dict()                              # script functions, key 'file.function'
        self.mdl = dict()                               # module used for loading each file, key 'file'
        self.func_names = dict()                         # list of function names per file, key 'file'

        self.read_module()

    def reload( self ):
        ''' Reloads all scripts of this directory.
        '''
        wx.MessageBox( "Modules that are directly imported cannot be reloaded.", "Sorry..", wx.OK | wx.ICON_WARNING )

    def read_module(self):
        self.func_help.clear()
        self.func_obj.clear()
        self.mdl.clear()
        self.func_names.clear()

        print("Reading scripts from " + self._script_dir)

        files = ["test1.py", "test2.py"]  # Example files, replace with actual module files
         
        msg = ""
        for name, value in inspect.getmembers(self.module, predicate=inspect.ismodule):
            if name.startswith("_") or name.endswith("_"):  # skip all special names
                continue

            print( "---> " + name )
            error = self.read_single_file(name, value)
            if error:
                msg = msg + "\n" + error        
             
             
    def read_single_file(self, modname, modobj):
        ''' Import a python python file, and find all functions in it.
            A treeview item with the file name is created, and child nodes for each function.
            A reference is kept to all of the functions to call them later on.
        '''       
        try:            
            self.mdl[modname] = modname
            self.func_names[modname] = list()
             
            for funcname, funcobj in  inspect.getmembers(modobj, predicate=inspect.isfunction):
                 
                doctxt = funcobj.__doc__ or ""                                  # get docstring of function
                if not doctxt:                                                      # skip functions without comment    
                    continue
                 
                if not ("@public" in doctxt) and not ("\\public" in doctxt):       # only functions with 'public' tag
                    continue
 
                doctxt = doctxt.replace("@public","").replace("\\public","")

                if doctxt:                                                          # remember function help, if any
                    self.func_help["%s.%s" % (modname,funcname)] = doctxt            
                else:
                    self.func_help["%s.%s" % (modname,funcname)] = "No help"
                     
                self.func_obj["%s.%s" % (modname,funcname)] = funcobj                      # remember reference to function
                self.func_names[modname].append(funcname)                            # remember function name for this file    

        except:
            msg = traceback.format_exc()               
            wx.MessageBox( msg, "Error importing file %s" % (modname), wx.OK | wx.ICON_WARNING )
             
        for fname in list(self.func_names.keys()):                               # delete all files without script functions
            if len(self.func_names[fname]) == 0:
                del self.func_names[fname]
             
        return None

    #============================================================================================================
    #                     Functions used by the GUI to get script info
    #============================================================================================================

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

