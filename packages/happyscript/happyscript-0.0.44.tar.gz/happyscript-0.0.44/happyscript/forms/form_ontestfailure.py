

import wx
from .formsbase import FormOnTestFailure_Base

class FormOnTestFailure( FormOnTestFailure_Base):
    ''' Form asking what to do after failure
    '''

    static_item = None

    @classmethod
    def show(cls, testname):
        ''' Instantiates the form if necessary (done only once).
            then shows the dialog as a modal dialog.
            
            Returns wx.ID_RETRY, wx.ID_FORWARD or wx.ID_STOP
        '''
        
        if cls.static_item is None:
            cls.static_item = FormOnTestFailure()
            
        cls.static_item.m_txtMessage.Label = "Test '%s' failed.\nWhat do you want to do ?" % testname
        cls.static_item.ShowModal()
        
        return cls.static_item.result
    
    @classmethod
    def cleanup(cls):
        ''' destroys form upon application end exit.
        '''
        if cls.static_item is not None:
            cls.static_item.Destroy()
            cls.static_item = None

    def __init__( self ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param dirname  Directory name to reads scripts from.
        '''
        super().__init__(None)
        self.result = wx.ID_STOP

    def OnBtnRetry( self, event ):
        self.result = wx.ID_RETRY
        self.Close()

    def OnBtnSkip( self, event ):
        self.result = wx.ID_FORWARD
        self.Close()

    def OnBtnStop( self, event ):
        self.result = wx.ID_STOP
        self.Close()

#stop-amalgamation

if __name__=="__main__":
    
    import wx
    app = wx.App()
    
    form = FormOnTestFailure(None)
    
    form.Show()
    
    app.MainLoop()
