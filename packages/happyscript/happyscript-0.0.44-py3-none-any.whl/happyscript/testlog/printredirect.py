#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import sys
import logging  
        
class PrintRedirect:
    ''' Class to handle redirection of print() output.
        Output is send to callback functions.
        Output is also written to logfile.
        Note that when the print() statement is in a different thread, then the logging functions will
        also be called from that thread, and any further processing as well (e.g. in log and message panels).
    '''
    
    _redir = None                                   # instance for redirecting print()
    _reerr = None                                   # instance for redirecting errors
    _old_redir = None                               # original destination for print and errors
            
    def __init__(self, globalloghandler, level=None):
        ''' Constructor.
            @param globalloghandler   The GlobalLogHandler object that puts all text on a queue for the GUI
            @param level              Default level.  Normally 'info', could be logging.ERROR for stderr
        '''
                       
        self.level = logging.INFO if level is None else level
        self.loghandler = globalloghandler
            
    def write(self,txt):
        txt = txt.strip()
        if txt=='\n' or len(txt)==0:
            return
        
        if self.level==logging.ERROR and txt=="^":          # ignore ^^^ marks of exception
            return
        
        level = self.level
        if "[FAIL]" in txt:
            level = logging.ERROR
            txt = txt.replace("[FAIL]","").strip()
        elif "[ERROR]" in txt:
            level = logging.ERROR
            txt = txt.replace("[ERROR]","").strip()
        elif "[PASS]" in txt:
            level = logging.WARN+1
            txt = txt.replace("[PASS]","").strip()
        elif "[WARN]" in txt:
            level = logging.WARN
            txt = txt.replace("[WARN]","").strip()
        
        self.loghandler.add_line_from_print(txt, level)

    def flush(self):
        pass

    @classmethod
    def start_redirection(cls, handler):
        ''' Starts redirecting text to the message area.
        '''
        cls._redir = PrintRedirect(handler)                    # redirect objects for stdout and sterr
        cls._reerr = PrintRedirect(handler,logging.ERROR)
        cls._old_redir = ( sys.stdout, sys.stderr )     # remember original targets
        sys.stdout=cls._redir                           # set new targets
        sys.stderr=cls._reerr
    
    @classmethod
    def stop_redirection(cls):
        if cls._old_redir is not None:
            sys.stdout, sys.stderr = cls._old_redir
            cls._old_redir = None


