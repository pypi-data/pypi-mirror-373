#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import wx
import datetime, logging
from .panelsbase import PanelMessages_Base

class PanelMessages( PanelMessages_Base ):
    ''' Panel with messages to display to test operator.
    '''
    
    def __init__( self, parent ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
        '''
        PanelMessages_Base.__init__(self, parent)
        
        self.lstMessages.InsertColumn(0, "Time", wx.LIST_FORMAT_RIGHT)
        self.lstMessages.InsertColumn(1, "Status")
        self.lstMessages.InsertColumn(2, "Message")
        
        self.lstMessages.SetColumnWidth(0, 75)
        self.lstMessages.SetColumnWidth(1, 70)
        self.lstMessages.SetColumnWidth(2, 100)
        
        self.loglevel = logging.WARN+1
    
    def clear(self):
        ''' Clear all messages from the list.
        '''
        self.lstMessages.DeleteAllItems()

    def OnListSize( self, event ):
        ''' Adjust width of 'Message' column upon resizing the panel.
        '''
        width = self.GetClientSize().width
        if width<160:
            width = 160;
        self.lstMessages.SetColumnWidth(2, width-150)    
        event.Skip()

    def HandleLogData(self, logdata):
        ''' Handles logdata from the GlobalLogHandler.
            This is called by the 
        '''
        if logdata.levelno < self.loglevel:             # skip if log level too low
            return
        
        if logdata.levelno>=logging.ERROR:           # error and critical in red
            color = wx.RED
        elif logdata.levelno==logging.WARN+1:        # warn+1 is custom level 'PASS'
            color = wx.BLUE
        elif logdata.levelno>=logging.WARN:          # warning in orange
            color = wx.Colour(255, 128, 0)
        else:
            color = None
        
        self.AddListEntry(logdata.levelname, logdata.msg, color)
                
        
    def AddListEntry(self, result, msg, color=None):
        ''' Adds a message to the list.
        
            @param result    tag for the 'result' column, e.g. PASS, FAIL
            @param msg       single-line text message
            @param color     optional, color (wx....) for text
        '''

        tstamp = datetime.datetime.now().strftime("%m/%d %H:%M")    # make output fields
        
        self.lstMessages.Append( (tstamp, result, msg) )        # add fields to table
        
        cnt = self.lstMessages.GetItemCount()
        
        if color is not None:                                   # change color if necessary
            item = self.lstMessages.GetItem(cnt-1)
            item.SetTextColour(color)
            self.lstMessages.SetItem(item)
        
        self.lstMessages.EnsureVisible(cnt - 1)         # make last row visible

        self.lstMessages.Update()                       # force update of control
                    
    # Virtual event handlers, overide them in your derived class
    def OnBtnClearList( self, event ):
        self.clear()
        
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
    