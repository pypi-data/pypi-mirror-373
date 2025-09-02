
import re
import wx
from .formsbase import FormSerials_Base

class FormSerials( FormSerials_Base):
    ''' Ask for up to 10 serial numbers.
        A label and match pattern can be given for each number.
        Result is a list of the serials, or None if user cancelled.
    '''

    static_item = None

    @classmethod
    def show(cls, count, labels = None, filters=None):
        ''' Instantiates the form (if necessary), then shows it.
        
            @param   count   how many numbers : 1 - 10 numbers
            @param   labels  List of strings to show left from each serial number entry field
            @param   filters regular expression for each serial number.  Items can be None
            @return  list of serial numbers, or None if no user cancelled
        '''
        
        if count<1 or count>10:
            return None
        
        if cls.static_item is None:
            cls.static_item = FormSerials()
        
        return cls.static_item.ask_serials(count, labels, filters)

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
        
        self.labels = [ self.m_lblSerial1, self.m_lblSerial2, self.m_lblSerial3, self.m_lblSerial4, self.m_lblSerial5,
                        self.m_lblSerial6, self.m_lblSerial7, self.m_lblSerial8, self.m_lblSerial9, self.m_lblSerial10 ]
        self.texts = [ self.m_txtSerial1, self.m_txtSerial2, self.m_txtSerial3, self.m_txtSerial4, self.m_txtSerial5,
                        self.m_txtSerial6, self.m_txtSerial7, self.m_txtSerial8, self.m_txtSerial9, self.m_txtSerial10 ]
        
        self.result = False

    def ask_serials(self, count, labels, filters ):
        ''' Called from class function show() to show the dialog.
            Initializes everything, shows the dialog, and then determines the result to return.
        '''
        
        if count<1 or count>10:
            return None
            
        self.initializing = True                                    # to silence event handlers on editboxes
            
        if labels is None:                                          # default labels
            labels = [ "Board 1", "Board 2", "Board 3", "Board 4", "Board 5", "Board 6", "Board 7", "Board 8", "Board 9", "Board 10" ] 

        if filters is None:                                         # default filters = all None
            self.filters = [ None, None, None, None, None, None, None, None, None, None ]
        else:
            self.filters = filters

        self.valid = list()                                         # list of validity of each serial
        
        for i in range(count):
            self.texts[i].Value = ''                                # initialize UI elements
            self.labels[i].Label = labels[i]
            self.texts[i].Show()
            self.labels[i].Show()
            self.texts[i].SetBackgroundColour(wx.Colour(255,204,204))
            
            if self.filters[i] is not None:                         # compile regex, if any
                self.filters[i] = re.compile(self.filters[i])
            
            self.valid.append(False)                                # init list with validity
            
        for i in range(count,10):                                    # hide unused serials
            self.texts[i].Hide()
            self.labels[i].Hide()
            
        self.m_btnOK.Disable()                                      # disable OK upon start
        self.initializing = False
        
        if self.ShowModal() != wx.ID_OK:
            return None
        if False in self.valid:
            return None
        
        serials = list()                                            # compose list of serials to return
        for i in range(count):
            serials.append( self.texts[i].Value.strip() )
        return serials

    def handle_ontext(self, num):
        ''' Checks serial numbers whenever the text in on of the text boxes changes.
            Color will be updated to green or red to indicate validity.
            'OK' button is enabled accordingly.
        '''
        if self.initializing or num<0 or num>9:
            return

        txt = self.texts[num].Value.strip()
        valid = False
        
        if len(txt)==0:
            valid = False
        elif self.filters[num] is not None:
            valid = True if self.filters[num].search(txt) else False
        else:
            valid = True
            
        self.texts[num].SetBackgroundColour( wx.Colour(204,255,204) if valid else wx.Colour(255,204,204) )
        self.valid[num] = valid
            
        if not self.m_btnOK.IsEnabled() and not (False in self.valid):
            self.m_btnOK.Enable()
        elif self.m_btnOK.IsEnabled() and (False in self.valid):
            self.m_btnOK.Disable()
            
        self.Update()
        self.Refresh()

    def OnText1( self, event ):
        self.handle_ontext(0)

    def OnText2( self, event ):
        self.handle_ontext(1)

    def OnText3( self, event ):
        self.handle_ontext(2)

    def OnText4( self, event ):
        self.handle_ontext(3)

    def OnText5( self, event ):
        self.handle_ontext(4)

    def OnText6( self, event ):
        self.handle_ontext(5)

    def OnText7( self, event ):
        self.handle_ontext(6)

    def OnText8( self, event ):
        self.handle_ontext(7)

    def OnText9( self, event ):
        self.handle_ontext(8)

    def OnText10( self, event ):
        self.handle_ontext(9)

    def handle_enter(self, num):
        ''' Moves to next field upon pressing enter in a serial number text field.
        '''
        if self.initializing or num<0 or num>9:
            return
    
        if num==9 or not self.texts[num+1].IsShown():
            self.m_btnOK.SetFocus()
        else:
            self.texts[num+1].SetFocus()

    def OnEnter1( self, event ):
        self.handle_enter(0)

    def OnEnter2( self, event ):
        self.handle_enter(1)

    def OnEnter3( self, event ):
        self.handle_enter(2)

    def OnEnter4( self, event ):
        self.handle_enter(3)

    def OnEnter5( self, event ):
        self.handle_enter(4)

    def OnEnter6( self, event ):
        self.handle_enter(5)

    def OnEnter7( self, event ):
        self.handle_enter(6)

    def OnEnter8( self, event ):
        self.handle_enter(7)

    def OnEnter9( self, event ):
        self.handle_enter(8)

    def OnEnter10( self, event ):
        self.handle_enter(9)

    def OnBtnCancel( self, event ):
        self.EndModal(wx.ID_CANCEL)

    def OnBtnOK( self, event ):
        self.EndModal(wx.ID_OK)
        
#stop-amalgamation

if __name__=="__main__":
    
    import wx
    app = wx.App()
        
    result = FormSerials.show(3, ["Logic Board", "Power board", "Micro ZED"],
                      [r'([0-9])\w+', None, r'([0-9])\w+'] )
    
    print(result)
