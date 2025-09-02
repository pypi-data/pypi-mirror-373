#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object for some flow control during a script
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

# import wx
import time

from .scriptexceptions import ScriptUserAbortException

class ScriptControl:
    ''' object to allow flow control during script execution
    '''
    def __init__(self):
        self.m_stop_script = False               # must the script stop ?
        self._is_busy = False
        self._script_runner = None

    def set_script_runner(self, runner):
        '''  !!! Internal use only !!!
             sets the ScriptRunner object that is used for running scripts
        '''
        self._script_runner = runner

    def set_busy(self, is_busy):
        '''  !!! Internal use only !!!
        '''
        self._is_busy = is_busy
        self.m_stop_script = False

    def is_busy(self):
        '''  !!! Internal use only !!!
        '''
        return self._is_busy

    def stop(self):
        '''  !!! Internal use only !!!
        '''
        if self._is_busy:
            print("'stop' flag is set.  Scripts may stop soon.")
        else:
            print("Normally no script is active, but I'll set the 'stop' flag anyway.")
        self.m_stop_script = True

    def ok(self) -> bool:
        ''' To test if the script should stop.  ok() will return True until the 'stop' button 
            is pressed.  Exit your script loop when ok() returns False.
        '''
        # wx.Yield()
        return not self.m_stop_script
    
    def check(self):
        ''' This function will check if the 'stop' button is pressed.
            If it is, an exception is raised, which will stop the script, and the script will
            be considered to have failed.
            Typically you call this regularly in a loop, so the script can be stopped
            without having to write a lot of code for error handling.
        '''
        # wx.Yield()
        if self.m_stop_script:
            raise ScriptUserAbortException( "Script stopping on user request" )

    def sleep(self, time_in_seconds : float):
        ''' Sleeps for the specified number of seconds.
            When the stop button is pressed, an exception will be raised and the
            script will be stopped (almost) immediately.
        '''
        t = time_in_seconds
        
        # wx.Yield()
        
        while t>0:
            if t > 0.5:
                time.sleep(0.5)
            else:
                time.sleep(t)
            t = t-0.5
            # wx.Yield()
            if self.m_stop_script:
                raise ScriptUserAbortException( "Script stopping on user request" )

    def run(self, script_name:str, **argv):
        ''' Execute a script from within another script.
            The script will be run in the same way as if it was started from the GUI.
            The script will run in the same thread as the calling script, so the calling
            script will be paused until the called script is finished.

            script_name is of the form "directory.file.function"

            You may pass arguments to the script using keyword arguments.  If the script
            needs additional parameters, ScriptManager will try to find these out by itself.
        '''
        assert self._script_runner is not None, "Internal error: scriptrunner is not set"
        return self._script_runner.run_script(script_name, **argv)

    def run_parallel(self, func, parname, parvalues, **extra_params):
        ''' excecute a function in parallel using different values for a given parameter
        '''
        return self._script_runner.run_parallel(func, parname, parvalues, **extra_params)