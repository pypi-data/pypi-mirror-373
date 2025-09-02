
import wx
import os, sys, subprocess

__curdir = os.path.dirname(os.path.realpath(__file__))

def localfile(filename):                                                # return file in local dir
    return os.path.join(__curdir, filename)

class SplashMenuForm( wx.Frame ):

    def __init__(self, num_x, num_y, border = 50):

        if num_x<1: num_x = 2                                           # parameter check
        if num_y<1: num_y = 1
        self.num_x = num_x
        self.num_y = num_y

        wx.Frame.__init__ ( self, None, id = wx.ID_ANY, title = u"Menu", pos = wx.DefaultPosition, size = wx.Size( 629,523 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_SHAPED|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        disp = wx.Display(wx.Display.GetFromWindow(self))               # get screen size
        (x1, y1, sx, sy) = disp.GetGeometry()

        if border < 0: border = 30                                      # sanity check on border parameter
        if border*3 > sx or border*3 > sy: border = min(sx//6,sy//6)

        sx -= 2*border                                                  # calculate new window size and position it
        sy -= 2*border
        self.SetSize( x1 + border, y1 + border, sx, sy)


        bSizer16 = wx.BoxSizer( wx.VERTICAL )                           # top sizer for buttons and status bar

        gSizer2 = wx.GridSizer( num_y, num_x, 0, 0 )                    # gridsizer for the buttons

        self.buttons = list()                                           # keep all buttons in a list
        self.programs = dict()
        self.arguments = dict()

        for y in range(num_y):
            for x in range(num_x):
                if y==num_y-1 and x==num_x-1:
                    break

                btn = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0, name=f"{x},{y}" )
                btn.location = (x+1,y+1)
                gSizer2.Add( btn, 0, wx.ALL|wx.EXPAND, 5 )
                self.buttons.append(btn)

        self.btnExit = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        # self.btnExit.SetBitmap( wx.Bitmap( u"exit.png", wx.BITMAP_TYPE_ANY ) )
        gSizer2.Add( self.btnExit, 0, wx.ALL|wx.EXPAND, 20 )

        bSizer16.Add( gSizer2, 1, wx.EXPAND, 5 )                        # add gridsizer to top container
        self.SetSizer( bSizer16 )                                       # set top sizer for the window
        self.Layout()                                                   # arrange all sizers

        self.m_statusBar2 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )   # add statusbar

        self.Centre( wx.BOTH )

        for btn in self.buttons:                                        # hide all buttons until later
            btn.Hide()
            btn.Bind( wx.EVT_BUTTON, self.OnButton )

        # Connect Events
        self.SetButtonImage( self.btnExit, localfile("exit.png") )
        self.btnExit.Bind( wx.EVT_BUTTON, self.DoExit )


    def DoExit( self, event ):
        self.Destroy()                                              # delete the frame
        wx.GetApp().ExitMainLoop()


    def SetButtonImage(self, btn, filename):
        ''' Set the image for an imagebutton.
            The image is automatically scaled to fit the size of the button.
        '''
        margin = 10

        img = wx.Image(filename, type=wx.BITMAP_TYPE_ANY)   # load image     
        isize = img.GetSize()
        bsize = btn.GetSize()

        fx = (bsize.x-margin) / isize.x                        # factors to stretch image to max, hor or vert
        fy = (bsize.y-margin) / isize.y
        factor = min(fx,fy)

        img_x = int(isize.x * factor)                         # new size of image
        img_y = int(isize.y * factor)

        img = img.Scale(img_x, img_y)                       # scale the image

        bitmap = img.ConvertToBitmap()                      # make a bitmap out of it

        btn.SetBitmap( bitmap )

    def ReturnButton(self, x, y):
        ''' Get the button object at the given location.
        '''
        return self.buttons[ (x-1) + (y-1)*self.num_x]

    def set_button(self, x, y, image, program, arguments):
        ''' Set info for button.
        '''
        if x<1 or x>self.num_x or y<1 or y>self.num_y or (x==self.num_x and y==self.num_y ):
            raise ValueError(f"position {x} {y} is not a valid button position")
        
        btn = self.ReturnButton(x,y)
        self.SetButtonImage(btn, image)
        btn.Show()

        self.programs[(x,y)] = program
        self.arguments[(x,y)] = arguments

    def OnButton(self, event ):
        btn = event.GetEventObject()

        if btn.location not in self.programs:
            raise ValueError(f"Strange... nothing to do for button {btn.location}")        
        
        program = self.programs[btn.location]
        arguments = self.arguments[btn.location]

        # self.Iconize()
        self.Hide()

        try:
            cmd = [ sys.executable, program]
            cmd.extend(arguments)
            # print(cmd)

            os.chdir( os.path.dirname(program) )
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in result.stdout.decode("utf-8").splitlines():
                print(line)
            for line in result.stderr.decode("utf-8").splitlines():
                print(line)

        except FileNotFoundError as exc:
            print(f"Process failed because the executable could not be found.\n{exc}")
        except subprocess.CalledProcessError as exc:
            print(
                f"Process failed because did not return a successful return code. "
                f"Returned {exc.returncode}\n{exc}"
            )

        finally:
            # self.Restore()
            self.Show()
            self.Raise()
