'''
Created on 29 Sep 2023

@author: marcvanriet
'''

import logging
import time

class LogToXML(object):
    ''' Writes logs to an XML file.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.logfilename = "happyscript.log.xml"
        self.handle = None
        self.last_flush_time = time.time()
        
    def open(self):
        ''' Opens the log file if necessary.
        '''
        if self.handle is not None:
            return
            
        self.handle = open(self.logfilename, "a+")
        self.handle.write("****** STARTING XML FILE ********\n")
            
            
    def close(self):
        ''' Closes the logfile (if necessary).
            Trailing XML data will be written to complete the document.
        '''
        if self.handle is None:
            return
        
        self.handle.write("****** CLOSING XML FILE ********\n")
        self.handle.close()
        
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
    
            