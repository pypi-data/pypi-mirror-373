#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to manage script readout and execution
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import os, logging, time
import wx

from .forms.form_main import FormMain
from .panels.panel_scripts2 import PanelScripts2
from .scriptcontrol import ScriptControl
from .testlog.printredirect import PrintRedirect
from .scriptrunner import ScriptRunner
from .scriptparams import ScriptParams
from .scriptgui import ScriptGui
from .scriptinfo import ScriptInfo
from .forms.form_serials import FormSerials
from .testlog.global_log_handler import GlobalLogHandler
from .testlog.log_to_text import LogToText
from .modulereader import ModuleReader
from .inifile import IniFile
from .forms.form_settings import FormSettings

class StaticScriptManager(object):
    dialog = None
    logger = logging.getLogger("happyscript")

    __the_one_and_only_instance = None
    ini = IniFile

    def __init__(self, title=None, colors = None, use_yaml=False):
        '''
            Constructor
            
            @param  Optional title for main window.
            @param  Optional color scheme for test list.
                    0=green, 1=blue, 2=yellow, 3=grey, 4=orange, 5=darker blue 
        '''
        assert StaticScriptManager.__the_one_and_only_instance is None, "Only one instance of a ScriptManager can be created."
        StaticScriptManager.__the_one_and_only_instance = self

        fixedcolors = [ (226, 239, 217), (222, 235, 246), (255, 242, 204), (237, 237, 237), 
                        (251, 229, 213), (217, 226, 243) ]
        
        self.on_batch_start = None
        self.on_batch_end = None
        
        # self.logfile_handler = None
        self.logfiles_defined = False                       # was a logfile set by the user ?
        
        logging.getLogger().setLevel(logging.INFO)
        logging.addLevelName(logging.WARN+1, "PASS")

        self.loghandler = GlobalLogHandler()
        logging.getLogger().addHandler(self.loghandler)

        paramiko_log = logging.getLogger("paramiko")                    # don't show Paramiko logging 
        paramiko_log.propagate = False

        self.textlogoutput = LogToText()
        self.loghandler.add_callback(self.textlogoutput.handle_log)

        self.app = wx.App()                                          # initialize wxWidgets
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        self.dialog = FormMain(self)
        
        self.charts = self.dialog.chartsPane
        
        self.loghandler.add_callback(self.dialog.logPane.HandleLog)
        self.loghandler.add_callback(self.dialog.msgArea.HandleLogData)
        self.dialog.on_log_timer = self.on_log_timer
        
        self.ctrl = ScriptControl()                            # create script run control object
        self.gui = ScriptGui(self)                      # object for interaction with user during test
        self.dialog.on_gui_timer = self.gui.on_gui_timer 
        self.info = ScriptInfo( self.dialog.pnlTests, use_yaml ) 
        
#         self.info.set_filename("happyscript.yml")
        
        self._script_params = ScriptParams(self.gui)        # object for maintaining script parameters
        self._script_params.on_add_object = self._on_add_object
        
        self._script_readers = dict()
        self._script_runner = ScriptRunner(self._script_params, self._script_readers, self.ctrl)
        self.ctrl.set_script_runner( self._script_runner )
        
        self._script_params.add_objects( ctrl=self.ctrl, gui=self.gui, info=self.info, mngr=self )

        self.dialog.pnlTests.on_sequence_start_callback = self.handle_batch_start
        self.dialog.pnlTests.on_sequence_end_callback = self.handle_batch_end
        
        self.set_logfiles()                                     # use standard log file names

        if title is not None:                                   # customize title if needed
            self.dialog.Title = title
            self.dialog.pnlTests.Label = title
        
        if colors is not None and colors in range(len(fixedcolors)):    # customize window colors if needed 
            rgb = fixedcolors[colors]
            color = wx.Colour(rgb[0], rgb[1], rgb[2])
            self.dialog.pnlTests.SetBackgroundColour(color)
            self.dialog.msgArea.SetBackgroundColour(color)

        self.dialog.Show()

    def on_log_timer(self):
        self.loghandler.run_callbacks()

    def set_logfiles(self, fname = None, fdir = None, use_temp = False):
        ''' Set the filenames for normal logging and info file.
            @param  fname     filename for logging, without extension.  Default 'happyscript'
            @param  fdir      directory name, either relative or absolute.  Default './log'
            @param  use_temp  use .tmp as extension for logfile.  Will be renamed by close_logfiles()  
        '''
        if fdir is None:
            fdir = "./log"
        if fname is None:
            fname = "happyscript"
            
        # if self.logfile_handler is not None:
        #     logging.getLogger('').removeHandler(self.logfile_handler)
        #     self.logfile_handler.close()
        #     self.logfile_handler = None
            
        fname,_ = os.path.splitext(fname)               # remove extension from filename, if any
            
        if not os.path.exists(fdir):                    # make sure directory exists
            os.makedirs(fdir)
            
        # self.logfilename = os.path.join(fdir, fname + (".tmp" if use_temp else ".log") )  # determine log file
        #
        # self.logfile_handler = TestLogHandler(self.logfilename)
        # logging.getLogger('').addHandler(self.logfile_handler)
            
#         logging.basicConfig( filename = self.logfilename, level=logging.INFO, force=True)       # set log file name
        self.info.set_filename( os.path.join(fdir, fname+".yml") )                  # set info file name

        self.textlogoutput.set_filename( os.path.join(fdir, fname+".log"), use_temp = use_temp )
        
        self.logger.info("Writing log to %s" % os.path.join(fdir, fname+".log"))
        self.logfiles_defined = True
            
    def close_logfiles(self):
        ''' 'Closes' all logfiles by selecting default names for everything.
            If a 'tmp' extension was used for the logfile, it will be renamed to .log.
            Note that there must be no other .log-file, otherwise it will be deleted.
        '''
        
        # if self.logfile_handler is not None and self.logfilename.endswith(".tmp") and os.path.isfile(self.logfilename):  # need to rename tmp file ?
        #     logging.getLogger('').removeHandler(self.logfile_handler)
        #     self.logfile_handler.close()
        #     self.logfile_handler = None
        #
        #     fname, _ = os.path.splitext(self.logfilename)                           # name without extension
        #     if os.path.isfile(fname+".log"):                                # delete .log if it exists
        #         os.remove(fname+".log")
        #     os.rename(self.logfilename, fname+".log")                       # rename .tmp to .log

        self.set_logfiles()                                                 # use default names now
        self.logfiles_defined = False

    def stop_scripts(self):
        ''' Sets flag to ask the running script (if any) to terminate.
            The script should use the 'ctrl' object to check this flag.
        '''
        self.ctrl.stop()

    def clear_log(self):
        ''' Clear the 'log' and 'messages' windows.
        '''
        self.dialog.ClearLogs()

    @classmethod
    def _set_ini(cls, ini):
        ''' Set the IniFile class for appication settings read from an ini file.
            This method is called by the IniFile class when a .ini file is read.
        '''
        assert cls.__the_one_and_only_instance is not None, "ScriptManager must be instantiated before reading an ini file."
        cls.ini = ini

#============================================================================================================
#                             P A R A M E T E R S
#============================================================================================================

    def add_object(self, objName, theObject):
        ''' Add an object that can be used as parameter in the script functions.
        '''
        self._script_params.add_object( objName, theObject)
        
    def add_objects(self, *args, **kwargs):
        ''' Add an object that can be used as parameter in the script functions.
           See ScriptParams.add_objects()
        '''
        self._script_params.add_objects(*args, **kwargs)

    def _on_add_object(self, obj_name, obj_value):
        ''' Callback function for every object added to the script parameters.
        '''
        if obj_value is None:
            self.logger.warning( f"Object with name {obj_name} is None." )
        else:
            if obj_name not in ['mgnr', 'ctrl', 'gui', 'info']:
                self.logger.info("Added object %s" %obj_name)
            self.dialog.PushShellCommand("%s = _mngr_._script_params.get_param('%s')" % (obj_name, obj_name))

#============================================================================================================
#                    R E A D   M O D U L E                         
#============================================================================================================

    def add_module(self, module, group_name=None):
        ''' Reads scripts from a directory : not possible with StaticScriptManager.
        '''
        if group_name is None:                                  # if no name given, use module name
            group_name = module.__name__

        self.logger.info( "Adding scripts module %s" % group_name )
       
        reader = ModuleReader(module, group_name)           # create object to read scripts in this dir
        self._script_readers[group_name] = reader
                
        newPanel = PanelScripts2(self.dialog._nbk_scripts, reader, self.ctrl ) # create script panel
        self.dialog._nbk_scripts.AddPage( newPanel, group_name, False)                   # add it in dialog


#============================================================================================================
#                    R E A D   S C R I P T S                       
#============================================================================================================

    def add_scripts(self, script_dir, group_name = None):
        ''' Reads scripts from a directory : not possible with StaticScriptManager.
        '''
        raise NotImplementedError("Scripts cannot be loaded dynamically by StaticScriptManager.  Use ScriptManager instead.")

#============================================================================================================
#         A D D   T E S T   L I S T                             
#============================================================================================================

    def add_test(self, description, scriptname, **args):
        ''' Add a test to the test list.
        '''
#         self.dialog.add_test(description, scriptname)
        self.dialog.pnlTests.add_test( description, scriptname, **args )
        
    def add_tests(self, testlist):
        ''' Add several test at once.
            Teslist must contain tuples containing the description and the test name
        '''
        for x in testlist:
            if len(x)==3:
                self.add_test( x[0], x[1], **x[2] )
            elif len(x)==2:
                self.add_test( x[0], x[1] )
            else:
                self.logger.critical("Expected at least description and test name in test list.")

#============================================================================================================
#         C A L L B A C K S                             
#============================================================================================================

    @property
    def on_cmd_line(self):
        ''' sets the callback function for commands entered in the log window
        '''
        return self.dialog.logPane.callback

    @on_cmd_line.setter
    def on_cmd_line(self, value):
        ''' sets the callback function for commands entered in the log window
        '''
        self.dialog.logPane.callback = value


    def handle_batch_start(self):
        ''' Called by testlist form when test sequence is started.
        '''
        result = True
        self.info.clear()
        if self.logfiles_defined:
            self.close_logfiles()
        
        if not self.on_batch_start is None and callable(self.on_batch_start):
            result = self.on_batch_start()
            
        if not self.logfiles_defined:
            fname = "test_" + time.strftime("%y%m%d-%H%M%S")
            self.set_logfiles(fname, use_temp=True)
            
        return result

    def handle_batch_end(self):
        ''' Called by testlist form when test sequence is ended.
        '''
        if not self.on_batch_end is None and callable(self.on_batch_end):
            self.on_batch_end()

        self.info.update_file(True)
        self.close_logfiles()

#============================================================================================================
#         V A R I A                             
#============================================================================================================

    def ask_serials(self, count, labels = None, filters=None, add_to_info=True):
        ''' Show standard form for asking serial numbers.
            The serials will be (by default) filled in in info, clearing any previous serials.
        
            @param   count   how many numbers : 1 - 5 numbers
            @param   labels  List of strings to show left from each serial number entry field
            @param   filters regular expression for each serial number.  Items can be None
            @return  list of serial numbers, or None if no user cancelled
        '''
        serials = FormSerials.show(count, labels, filters)
        
        if add_to_info:
            self.info.set_serials(serials)
            
        return serials
    
    def add_custom_panel(self, title, panelType, **args):    
        ''' Add a custom panel to the pane with control panels.
            The panel constructor MUST have a parameter named 'parent'.  This will be filled in 
            automatically with the object containing the new panel. 
        
            @param  Title        Title for the panel
            @param  panelType    class to instantiate
            @param  args         parameters to supply to the constructor of the class
            @return The newly created panel
        '''
        return self.dialog.AddCustomPanel(title, panelType, **args)
        
    def show_settings(self):

        FormSettings.show_modal(self.dialog, self.ini)
        

#============================================================================================================
#          S T A R T    A P P L I C A T I O N                   
#============================================================================================================
        
    def run(self):
        ''' Starts the application.
            Not to be confused with ScriptPanelRunner.run(), which is used to run a script.
        '''
        if self.ini._get_configparser() is None:            # if no ini file set, disable the settings button
            self.dialog.DisableSettingsButton()

        self.dialog.BeforeShow()                                # restores previous layout of dialog 
#         PrintRedirect.set_logfile("happyscript.log")
        PrintRedirect.start_redirection(self.loghandler)                       # redirect print output to message area
        print("Happyscript started")

        self.app.MainLoop()                                     # starts wxWidgets main loop
        
        PrintRedirect.stop_redirection()
        
        self.info.update_file(True)                             # make sure all info (if any) is written
        self.textlogoutput.close()
        


