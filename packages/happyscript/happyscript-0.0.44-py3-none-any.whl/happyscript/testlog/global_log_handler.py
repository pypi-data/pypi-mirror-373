#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import logging, traceback
import queue

class LogData():
    
    msg = ""
    levelno = 0
    levelname = "[?]"
    exc_info = None
    
class PanelFormatter(logging.Formatter):
    ''' Composes a single string with log text to show to the user.
        Main use here is to expand the message if arguments were specified.
    '''
    def __init__(self): 
        super().__init__()
 
    def format(self, record):
        if len(record.args) > 0:
            try:
                msg = record.msg % record.args
            except TypeError:
                msg = record.msg + " !!! BAD PARAMETERS !!! " + str(record.args)
        else:
            msg = record.msg
        
        # if record.levelno >= logging.WARN:
        #     return "[%s] %s" % (record.levelname, msg)
        # else:
        return msg

class GlobalLogHandler(logging.StreamHandler):

    def __init__(self):
        super().__init__(None)

#         formatter = logging.Formatter("[%(levelname)s] %(message)s")
        formatter = PanelFormatter()
        self.setFormatter(formatter)
        self._callbacks = list()
        self._queue = queue.Queue()
        
    
    def add_callback(self, func):
        ''' Add a callback function to be called when something is logged.
            Callback function must accept a LogData structure as parameter.
        '''
        self._callbacks.append(func)
    
    def run_callbacks(self):
        ''' Executes the callback functions for all the items in the queue.
            This must be called regularly from the GUI thread.
        '''
        while not self._queue.empty():
            data = self._queue.get()
            for func in self._callbacks:
                try:
                    func(data)
                except:
                    pass
                
    def emit(self, record):
        ''' Called when something is logged.
            This is executed in the thread of the calling function.  Therefore we just always
            put the log on the queue, and the queue will be emptied regularly in the GUI thread.
        '''
        data = LogData()                                    # new structure with log info
        
        data.levelname = record.levelname                   # fill in most common log info
        data.levelno = record.levelno
        data.msg = self.format(record)
        
        # if there is an exception, make a multi-line text string with readable exception info
        if record.exc_info and str(record.exc_info[1])!="'Stopping parent script...'":
            exc_info = None
            tb = traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])
            for line in tb[:-1 or None]:
                if line.startswith("Traceback "):
                    continue
                if "in execute_threadfunc" in line:
                    continue

                if exc_info is None:
                    exc_info = line
                else:
                    exc_info += "\r\n" + line
            data.exc_info = exc_info

        self._queue.put(data)                               # put log on queue for later processing

    def add_line_from_print(self, msg, level):
        ''' Method to be used by the printredirect class to transfer a printed text
            to the global log handler.
        '''
        data = LogData()
        data.levelno = level
        data.levelname = logging.getLevelName(level)
        data.msg = msg

        self._queue.put(data)                               # put log on queue for later processing

