'''
Created on 29 Sep 2023

@author: marcvanriet
'''

import logging
import time
import os

class LogToText(object):
    ''' Writes logs to a text file.
    
        Flush() is called regularly so that output is not lost if the program crashes.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.logfilename = "happyscript.log"
        self.tempfilename = self.logfilename
        self.handle = None
        self.last_flush_time = time.time()                  # when was output last flushed ?
        
    def set_filename(self, filename, /, use_temp=False):
        ''' Sets the file name for log output.
            If the file already exists, output is appended.
            If it doesn't exist, it is created.
            If a directory name is used, it must exist.
        '''
        self.close()
        
        self.logfilename = filename
        
        if use_temp:
            self.tempfilename = os.path.splitext(filename)[0] + ".tmp"
        else:
            self.tempfilename = filename
        
    def open(self):
        ''' Opens the log file if necessary.
        '''
        if self.handle is not None:
            return
            
        self.handle = open(self.tempfilename, "a+")
        self.last_flush_time = time.time()
        self.handle.write("****** STARTING log FILE ********\n")
            
            
    def close(self):
        ''' Closes the logfile (if necessary).
            Trailing XML data will be written to complete the document.
        '''
        if self.handle is None:
            return
        
        self.handle.write("****** CLOSING log FILE ********\n")
        self.handle.close()
        
        if self.logfilename!=self.tempfilename:                     # we are using a .tmp file
            if os.path.isfile(self.logfilename):                    # remove old .log file if it exists
                os.remove(self.logfilename)
            if os.path.isfile(self.tempfilename):                    # rename .tmp file to real name
                os.rename(self.tempfilename, self.logfilename)
        
        self.handle = None
        
    def handle_log(self, logdata):
        ''' Process log entry.
        '''
        self.open()

        # if logdata.levelno < self.loglevel:             # skip if log level too low
        #     return
        
        msg = logdata.msg.strip()
        if logdata.levelno >= logging.WARN:
            self.handle.write(f"{logdata.levelname}: {msg}\n")
        else:
            self.handle.write(msg+"\n")
            
        if logdata.exc_info is not None:
            self.handle.write(logdata.exc_info)
        
        t = time.time()
        if t - self.last_flush_time > 5:
            self.handle.flush()
            self.last_flush_time = t
    
