
import wx

from .formsbase import FormAskChoice_Base

class FormAskChoice( FormAskChoice_Base):
    ''' Form for asking the operator to select something from a list
    '''

    def __init__( self, message, choices ):
        ''' constructor
        '''
        super().__init__(None)
        self.m_txtMessage.Label = message                   # show the text message
        self.m_txtMessage.Wrap(self.m_txtMessage.Size.Width)

        self.SetSize( 320, 175 + len(choices*75))
            
        self.buttons = list()

        bSizer22 = wx.BoxSizer( wx.VERTICAL )        
        
        for x in choices:
            
            btn = wx.Button( self.m_pnlChoices, wx.ID_ANY, x, wx.DefaultPosition, wx.DefaultSize, 0|wx.BORDER_NONE )
            btn.SetFont( wx.Font( 12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
            btn.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
     
            btn.Bind( wx.EVT_BUTTON, self.OnTestClick )     
            bSizer22.Add( btn, 1, wx.ALL|wx.EXPAND, 5 )
            
            self.buttons.append(btn)

        self.m_pnlChoices.SetSizer( bSizer22 )
        self.m_pnlChoices.Layout()
        bSizer22.Fit( self.m_pnlChoices )
        
        self.result = -1


    def OnTestClick( self, event ):
        
        btn = event.GetEventObject()
        pos = self.buttons.index(btn)
        
        for i in range(len(self.buttons)):
            if self.buttons[i] == btn:
                self.buttons[i].SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )
                self.buttons[i].SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
                self.result = i
            else:
                self.buttons[i].SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
                self.buttons[i].SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNTEXT) )
                
        self.m_btnOK.Enable()

    # Virtual event handlers, overide them in your derived class
    def OnButtonOK( self, event ):
        self.EndModal(wx.ID_OK)
        
    def OnButtonCancel( self, event ):
        self.result = -1
        self.EndModal(wx.ID_CANCEL)

#stop-amalgamation

if __name__=="__main__":
    
    app = wx.App()
    
    form = FormAskChoice("Dit is een test van een hele lange zin.", ["Test1", "Test2 ", "Test 3", "TEST 5"])
    
    form.ShowModal()
    print( form.result )
    
    app.MainLoop()
