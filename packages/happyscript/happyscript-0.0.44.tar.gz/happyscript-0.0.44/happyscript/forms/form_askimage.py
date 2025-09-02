
import wx

from .formsbase import FormAskImage_Base

class FormAskImage( FormAskImage_Base):
    ''' Form for asking something to operator
    '''

    def __init__( self, message, filename, arrow_pos=None, yesno=False, cancel=False, numeric=False ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param dirname  Directory name to reads scripts from.
        '''
        super().__init__(None)
        self.m_txtMessage.Label = message                   # show the text message
                
        self.numeric = numeric
        self.yesno = yesno
        self.result = None                                  # stores result 
        
        if yesno:                                      # show either input field or no button
            self.m_btnOK.Label = "Yes"
            self.m_txtValue.Hide()
        else:
            self.m_btnNo.Hide()
        
        if not cancel:                                      # hide cancel button if not used
            self.m_btnCancel.Hide()

        img = wx.Image(filename, type=wx.BITMAP_TYPE_ANY)   # load image        

        (img_x, img_y) = img.GetSize()                      # get image size
        disp = wx.Display(wx.Display.GetFromWindow(self))
        (x1, y1, sx, sy) = disp.GetGeometry()               # get screen starting point and size
                
        fx = (sx*9/10 - 200) / img_x                        # factors to stretch image to max, hor or vert
        fy = (sy*9/10 - 50) / img_y
        
        if fx<fy:                                           # determine factor to scale, either hor or vert
            factor = fx
        else:
            factor = fy

        img_x = int(img_x * factor)                         # new size of image
        img_y = int(img_y * factor)

        img = img.Scale(img_x, img_y)                       # scale the image

        bitmap = img.ConvertToBitmap()                      # make a bitmap out of it

        self.draw_arrow(bitmap, arrow_pos, factor)

        self.m_bitmap.SetBitmap(bitmap)                                 # show bitmap on window

        self.SetSize( x1 + (sx - img_x - 220)//2, y1 + (sy-img_y-70)//2, img_x + 220, img_y + 70)   # position the window
        self.m_txtMessage.Wrap(self.m_txtMessage.Size.Width)

    def draw_arrow(self, bitmap, arrow_pos, scale=1.0):
        ''' Draw an arrow to a point of interest.
            Arrow direction is adapted in case point is too close to right or bottom edge.
        ''' 
        if arrow_pos is None:
            return
            
        ax = int( arrow_pos[0] * scale ) 
        ay = int( arrow_pos[1] * scale )
    
        (max_x, max_y) = bitmap.GetSize()                      # get image and screen size            

        fx = 1 if ax+100 < max_x else -1
        fy = 1 if ay+100 < max_y else -1
        
        dc = wx.MemoryDC(bitmap)
        dc.SetPen(wx.Pen(colour='red', width=8, style=wx.SOLID))
        dc.DrawLine(ax, ay, ax+100*fx, ay+100*fy)
        dc.DrawLine(ax, ay, ax+30*fx, ay+10*fy)
        dc.DrawLine(ax, ay, ax+10*fx, ay+30*fy)
        del dc

    # Virtual event handlers, overide them in your derived class
    def OnButtonOK( self, event ):
        if self.numeric:            
            try:
                self.result = float(self.m_txtValue.Value) 
                self.EndModal(wx.ID_OK)
            except ValueError:
                wx.MessageBox(f"'{self.m_txtValue.Value}' is not a valid number")
                
        elif self.yesno:
            self.result = True
            self.EndModal(wx.ID_OK)
            
        else:
            self.result = self.m_txtValue.Value
            self.EndModal(wx.ID_OK)
        
    def OnButtonNo( self, event ):
        self.result = False
        self.EndModal(wx.ID_NO)

    def OnButtonCancel( self, event ):
        self.EndModal(wx.ID_CANCEL)

#stop-amalgamation


if __name__=="__main__":
    
    app = wx.App()
    
    form = FormAskImage("Dit is\n een test.", "demo_pcb.jpg", (50,600), yesno=False, cancel=True, numeric=True)
    
    form.ShowModal()
    
    app.MainLoop()
