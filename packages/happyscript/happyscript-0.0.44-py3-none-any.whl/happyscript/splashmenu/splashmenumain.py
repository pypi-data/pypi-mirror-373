
import os

class SplashMenu():

    def __init__(self, mainfilename, num_x, num_y, border = 50):
        ''' Constructor.
            mainfilename : the __file__ of your main program
            num_x,num_y : number of buttons in X (horizontal) and Y (vertical) direction
            border : border in pixel to use all around the form
        '''

        import wx
        from .splashmenuform import SplashMenuForm

        self.mainfile = mainfilename
        self.maindir = os.path.dirname(os.path.abspath(mainfilename))

        self.app = wx.App()
        self.top = SplashMenuForm(num_x, num_y, border)

    def set_button(self, x, y, image, program, arguments=None):
        ''' Defines program to execute for a button.
            x,y : location of button, 1,1 = top-left
            image = image to show on button
            program = python file to run
            arguments = argument or list of arguments to supply to python file
        '''
        imgfile = os.path.join(self.maindir, image)                 # determine absolute path of image
        if not os.path.exists(imgfile):
            imgfile = os.path.abspath(image)
            if not os.path.exists(imgfile):
                raise ValueError( f"Could not find file {image}")
            
        progfile = os.path.join(self.maindir, program)              # determine absolute path of python file
        if not os.path.exists(progfile):
            progfile = os.path.abspath(program)
            if not os.path.exists(progfile):
                raise ValueError( f"Could not find file {program}")
        
        if arguments is None:                                       # make sure arguments are a list
            arguments = list()
        elif type(arguments) is not list:
            arguments = [ arguments ]

        for i in range(0,len(arguments)):                           # make sure arguments are strings
            if type(arguments[i]) is not str:
                arguments[i] = str(arguments[i])

        self.top.set_button(x, y, imgfile, progfile, arguments)     # set info for button in the form

    def run(self):
        ''' Show the mainform.
        '''
        self.top.Show()
        self.app.MainLoop()

