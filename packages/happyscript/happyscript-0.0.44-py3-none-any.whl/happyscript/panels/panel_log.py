#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import wx
import logging

from .panelsbase import PanelLog_Base

class PanelLog( PanelLog_Base ):
    ''' Panel with logging of all output with print().
        Also contains a command line to give user commands.
    '''

    def __init__( self, parent ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param dirname  Directory name to reads scripts from.
        '''
        super().__init__(parent)
     
        self.lstCommandHistory = list()                 # list of previous commands
        self.posInCommandHistory = 0                    # which command we last restored
        
        self.callback = None
        self.first_time_in_commandline = True
        self.loglevel = logging.INFO
        self._stop_log = False
        
    def clear(self):
        ''' Clear the output.
            Must be called from the GUI thread, not from a script thread.
        '''
        self.wx_txtLog.Clear()

    def OnBtnClearLog( self, event ):
        ''' Clears all text in the log window.
        '''
        self.clear()
        
    def HandleLog(self, logdata):
        ''' Show given log in the output window.    
            Called from the global log handler
        '''
        if logdata.levelno < self.loglevel:             # skip if log level too low
            return
        
        if self._stop_log:                              # logging was stopped
            return

        if logdata.levelno >= logging.WARN:
            self.wx_txtLog.AppendText(f"{logdata.levelname}: {logdata.msg}\r\n")
        else:
            self.wx_txtLog.AppendText(logdata.msg+"\r\n")
            
        if logdata.exc_info is not None:
            self.wx_txtLog.AppendText(logdata.exc_info)

    def OnSelectLogLevel( self, event ):
        sel = self.m_cboLogLevel.GetStringSelection().lower()
        
        if sel=="warning":
            self.loglevel = logging.WARN
        elif sel=="info":
            self.loglevel = logging.INFO
        else:
            self.loglevel = logging.DEBUG
            
            logger = logging.getLogger('')
            if logger.getEffectiveLevel() > logging.DEBUG:
                logger.setLevel(logging.DEBUG)            

    def OnBtnStop( self, event ):
        self._stop_log = True
        self.m_btnStop.Enable(False)
        self.m_btnResume.Enable(True)
        self.m_btnResume.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )


    def OnBtnResume( self, event ):
        self._stop_log = False
        self.m_btnStop.Enable(True)
        self.m_btnResume.Enable(False)
        self.m_btnResume.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

    def OnSetFocus( self, event ):
        if self.first_time_in_commandline:
            self.first_time_in_commandline = False
            self.wx_txtCommand.Clear()
        event.Skip()

    # Virtual event handlers, override them in your derived class
    def OnCmdKeyUp( self, event ):
        if len(self.lstCommandHistory)==0:                  # do nothing if no history yet
            return;
        
        key = event.GetKeyCode()                        # go to next or previous entry in history list
        if key == wx.WXK_UP:
            self.posInCommandHistory -= 1
        elif key== wx.WXK_DOWN:
            self.posInCommandHistory += 1
        else:
            return

        if self.posInCommandHistory<0:                  # make sure position is within boundary
            self.posInCommandHistory = 0
        elif self.posInCommandHistory>=len(self.lstCommandHistory):
            self.posInCommandHistory = len(self.lstCommandHistory)-1

        self.wx_txtCommand.Value = self.lstCommandHistory[self.posInCommandHistory]   # restore command


    def OnCmdEnter( self, event ):
        ''' Send present string on the command line to callback function
        '''
        if self.callback is None:
            print("[ERROR] no callback defined for when you type a command")
            return
        
        cmd = self.wx_txtCommand.GetValue().strip()

        if cmd not in self.lstCommandHistory:                       # add cmd to history if not already in it 
            self.lstCommandHistory.append(cmd)
            self.posInCommandHistory = len(self.lstCommandHistory)
        
        self.wx_txtCommand.Clear()
        self.callback(cmd)


