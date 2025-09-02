#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to manage script readout and execution
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import inspect
from .scriptexceptions import ScriptUserAbortException

class ScriptParams(object):
    ''' Maintains a collection of objects that can be provided as parameter to script functions.
    '''

    def __init__(self, ask_gui = None):
        ''' Constructor
            @param ask_gui    Object with functions for asking a parameter if it is specified in the comments.
        '''
        self._ask_gui = ask_gui
        self.argumentList = dict()                  # list of objects that can be passed to script functions
        self.on_add_object = None                   # callback function
        
    def add_object(self, objName, theObject):
        ''' Add an object that can be used as parameter in the script functions.
        '''
        objName = objName.lower().strip()
        if objName=="_mngr_" or (objName is None) or len(objName)==0 or not objName.isidentifier():
            self.on_add_object("invalid object name '%s' " % objName, None)
            return 
        elif theObject is None:
            self.on_add_object("Value for object %s is None" % objName, None)
            return
        
        self.argumentList[objName] = theObject
        if self.on_add_object is not None:
            self.on_add_object( objName, theObject )

    def add_objects(self, *args, **kwargs):
        ''' Add a number of objects.
            The name is derived from the keyword when using keyword arguments.
            When not using keyword arguments, the name is derived from a member  '__name__' that must be
            present for the object.  This is a convention, so this member must be explicitly added.
        '''
        for obj in args:
            if obj is None:
                continue
            try:
                if hasattr(obj, "name") and isinstance(obj.name, str):
                    self.add_object(obj.name, obj)
                elif hasattr(obj, "_name") and isinstance(obj._name, str):
                    self.add_object(obj._name, obj)
                elif hasattr(obj, "__name__") and isinstance(obj.__name__, str):
                    self.add_object(obj.__name__, obj)
            except AttributeError:
                self.on_add_object("No name found for object that was added", None)
                pass
                
        for key, value in kwargs.items():
            self.add_object(key, value)

    def get_param(self, param_name):
        ''' Get value of a parameter.
        '''
        if param_name in self.argumentList:
            return self.argumentList[param_name]
        else:
            return None

    def get_parameters(self, scriptObject, extraParams=None):
        ''' Executes a script function provided by a script treeview panel.
        
            @param scriptObject : the function to execute, as an object
            @param extraParams : dictionary of extra parameters that may be passed to the test function
        '''

        if (extraParams is None) or (not isinstance(extraParams,dict)):
            extraParams = dict()

        missing = list()
        argnames = inspect.getfullargspec(scriptObject)[0]           # get list of arguments
        doctxt = inspect.getdoc( scriptObject )                  # comment for the function
        argvalues = list()
        for x in argnames:
            if x in self.argumentList:
                argvalues.append( self.argumentList[x] )
            elif x in extraParams:
                argvalues.append( extraParams[x] )
            elif self._ask_gui is not None:
                argvalues.append( self._find_missing_parameter(x, doctxt) )
            else:
                argvalues.append( None )
                missing.append(x)
 
        return (argvalues, missing)

    def _find_missing_parameter(self, paramName, docTxt ):
        ''' If a parameter is not found, see from the functions comments if it should be asked using the GUI.
        '''
        if docTxt is None: return None
        
        result = None
        lines = docTxt.splitlines()
        for line in lines:
            if "@param " + paramName + " " in line:
                
                if ':' in line:                                     # see if help contains question for dialog
                    question = line[line.find(':')+1:].strip()
                else:
                    question = "Give parameter %s" % paramName
                
                try:
                    if '[num]' in line:                             # ask for a number
                        result = self._ask_gui.ask_number(question)
                    else:                                           # ask for a string
                        result = self._ask_gui.ask(question)
                except ScriptUserAbortException as _:               # return None if user pressed 'Cancel'
                    pass
                break

        return result
