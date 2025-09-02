#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to keep list of script panels and to execute scripts
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : N/A
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import datetime, logging, threading

from .scriptexceptions import ScriptUserAbortException
from .scriptexceptions import ScriptRecursiveAbortException

class ScriptThreadRunner:
    ''' Separate class for things related to running a script in a thread.
        Maintains a recursion counter to allow scripts calling one another, using a single thread.
    '''
    logger = logging.getLogger("happyscript.scriptrunner")
    MARKER_LEVEL = 25
    
    def __init__(self, ctrl):
        self._ctrl = ctrl                                                       # scriptctrl for setting the busy flag
        self._recurse_count = 0                                                 # counter for counting script recursion depth            
        self.top_script_name = ''                                               # name of the toplevel script
        self.last_result = False                                                # indicates if last test was OK
        self.busy = False 

    def execute_script(self, script_name, script_func, argvalues):
        ''' Executes a script function
        '''
        self.last_result = False
        self.busy = True
                
        if threading.currentThread().getName()=="ScriptThread":                         # script started from ScriptThread itself is OK
            self.execute_threadfunc(script_name, script_func, argvalues)
            
        elif self._recurse_count>0:                                                     # second script started while 1 is running
            self.logger.error( "Script '%s' already running.  Wait until it completed." % self.top_script_name )
                    
        else:                                                                           # no script active, start script in new thread
            self.top_script_name = script_name
            thread = threading.Thread(name = "ScriptThread", target=self.execute_threadfunc, args=(script_name, script_func, argvalues) )
            thread.start()    

    def execute_threadfunc(self, script_name, script_func, argvalues):
        '''
            Executes a script function
        
            @param script_name : name of the script, e.g. "demo.test_loop"
            @param script_func : the function to execute, as an object
            @param extra_params : dictionary of extra parameters that may be passed to the test function
        '''
        if self._recurse_count<0:                                # should never happen
            self._recurse_count = 0
            
        tstamp = datetime.datetime.now().strftime("%m/%d_%H:%M")
        self.logger.log(self.MARKER_LEVEL, "__________%s__________%s__" % (script_name, tstamp) )
        
        test_passed = False
        all_tests_done = False                                      # in case of recursion, are all done up to top parent script ?
        try:
            self._recurse_count += 1
            self._ctrl.set_busy(True)
            script_func( *argvalues )                               # execute the function with its parameters
            test_passed = True    
        except ScriptUserAbortException as _:
            self.logger.error("Script stopped by user")            
        except Exception as e:
            if self._ctrl.m_stop_script:
                self.logger.error("Script stopped by user")
            else:
                logging.error(str(e), exc_info = e)
        finally:
            self._recurse_count -= 1                                    # keep track of script recursion counter
            if self._recurse_count<=0:                              
                all_tests_done = True
                
            if test_passed:                
                self.logger.log(self.MARKER_LEVEL, "\\_________%s__________ PASS ______/" % script_name )
            else:
                self.logger.log(self.MARKER_LEVEL, "\\_________%s__________ FAIL ______/" % script_name )

        if self._recurse_count>0 and test_passed==False:                    # if called from parent script, stop it using exception
            raise ScriptRecursiveAbortException("Stopping parent script...")
        
        if all_tests_done:
            self._recurse_count = 0  
            self.top_script_name=''
            self.last_result = test_passed
            self._ctrl.set_busy(False)
            self.busy = False


class ScriptParallelThread(threading.Thread):

    thread_counter = 0

    def __init__(self, ctrl, func, arg_list):
        thread_name = "Parallel" + str(ScriptParallelThread.thread_counter)
        threading.Thread.__init__(self, name=thread_name)
        ScriptParallelThread.thread_counter += 1

        self._ctrl = ctrl
        self.the_func = func
        self.arg_list = arg_list
        self.success = False
        self.stopped_by_user = False
        # self.exc = None
        self.start()

    def run(self):
        ''' This will be executed when start() is called.
        '''
        try:
            self.the_func( *self.arg_list )                               # execute the function with its parameters
            self.success = True    
        except ScriptUserAbortException as _:
            pass
        except Exception as e:
            if self._ctrl.m_stop_script:
                self.stopped_by_user = True
            else:
                logging.error(str(e), exc_info = e)
                # self.exc = e


class ScriptRunner:
    ''' Class to allow easy running of scripts from code.
        
        Looks up the script function object in the ScriptReader class.
        Looks up the parameters in the ScriptParams class.
        Sets 'busy' flag for the ctrl object (in ScriptThreadRunner)
    '''
    logger = logging.getLogger("happyscript.runner")

    def __init__(self, script_params, script_readers, script_control):
        self.script_params = script_params
        self._readers = script_readers
        self._recurse_count = 0
        self.start_ok = False
        self._ctrl = script_control
        
        self.thread_runner = ScriptThreadRunner(script_control)

    @property
    def test_passed(self):
        return self.start_ok and self.thread_runner.last_result
    
    @property
    def busy(self):
        return self.thread_runner.busy

    def find_scriptfunct(self, script_name):
        ''' Find the script function, based on the dotted script name with
            directory name, filename, function name.
            Returns the script function, or None if it is not found.
        '''
        parts = script_name.split(".")                                  # split script name in parts
        if len(parts) != 3:
            self.logger.error("Must provide script name as dirname.filename.scriptname")
            return None

        if not parts[0] in self._readers:                               # check if scripts were read from that dir
            self.logger.error("Cannot start %s : group %s not found",  script_name, parts[0])
            return  None
        
        func = self._readers[parts[0]].get_func(parts[1], parts[2])     # find the function in the given file
        if func is None:
            self.logger.error("Cannot start %s : function not found", script_name)

        return func

    def run_script(self, script_name, **extra_params):
        ''' Start a script given the directory group_name, filename and function name.
        '''
        self.start_ok = False

        if threading.currentThread().getName().startswith("Parallel"):
            self.logger.error("You cannot start other scripts in a parallel thread.")
            return
        
        func = self.find_scriptfunct(script_name)                       # find script function
        if func is None: return

        (argvalues, missing) = self.script_params.get_parameters(func, extra_params)    # find arguments

        if len(missing)>0:                                  # an argument was not found
            self.logger.error( "Error : missing value for parameter(s) %s" % ("".join(missing) ) )
            return
                                
        self.thread_runner.execute_script(script_name, func, argvalues)
        self.start_ok = True

    def run_parallel(self, func, parname, parvalues, **extra_params):
        ''' Run a method in parallel, supplying different values to the given parameter.
        '''
        assert threading.currentThread().getName()=="ScriptThread", "run_parallel() can only be executed from within a (non-parallel) script function"

        if not callable(func):
            func = self.find_scriptfunct(func)                       # find script function
            assert func is not None, f"Parameter 'func' of run_parallel is no function or script name."

        threads = list()
        for val in parvalues:
            extra_params[parname] = val
            (argvalues, missing) = self.script_params.get_parameters(func, extra_params)    # find arguments

            if len(missing)>0:                                  # an argument was not found
                self.logger.error( "Error : missing value for parameter(s) %s" % ("".join(missing) ) )
                return
            
            threads.append( ScriptParallelThread(self._ctrl, func, argvalues) )

        fail_count = 0
        stopped_by_user = 0
        for thread in threads:                              # wait for all the threats to finish
            thread.join()
            if not thread.success:                          # count how many failed
                fail_count += 1
            if thread.stopped_by_user:                      # count how many have been manually stopped
                stopped_by_user += 1

        if stopped_by_user>0:
            self.logger.error(f"{stopped_by_user} scripts stopped by user")
        assert fail_count==0, f"Parallel executiong failed on {fail_count} threads"
        

