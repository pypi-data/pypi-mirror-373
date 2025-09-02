#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object for some flow control during a script
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import wx
import threading

from .scriptexceptions import ScriptUserAbortException
from .forms.form_askimage import FormAskImage
from .forms.form_askchoice import FormAskChoice
from .forms.form_stop import FormStop

from .charts.histogram_chart import HistogramChart
from .charts.scatter_chart import ScatterChart
from .charts.time_chart import TimeChart
from .charts.matplotlib_chart import MatPlotLibChart
from .charts.chart import Chart

class ScriptGui:
    ''' Object with various functions to interact with the user / operator.
    '''

    def __init__(self, mngr):
        self._mngr = mngr
        self.__func = None
        self.__params = None
        self.__reply = None
        self.__have_reply = threading.Semaphore(0)
        
        self.m_stop_dialog = None

    def on_gui_timer(self):
        ''' !!! Internal use only !!!
            timer function called regularly from the mainform in the GUI thread.
            Used as a way to start dialogs from a thread in the GUI thread.
        '''
        if self.__func is not None:                             # if __func is filled in, it means we must do something
            func = self.__func
            self.__func = None
            try:
#                 print("CALLBACK in thread %s" % threading.currentThread().getName())
                self.__reply = func(*self.__params)             # call __func with its parameters
            except Exception as e:
#                 print("Exception when executing callback")
                self.__reply = e                                # if exception occurred, store that as reply
  
            self.__have_reply.release()                         # signal that action is complete

    def __run_with_timer(self, func, *params):
        ''' Runs the given function in the GUI thread.
            Waits until the action has completed, and then returns the result
        '''
#         print("Going to run function with GUI timer")
        self.__params = params                                  # remember all info in class parameters; timer watches this
        self.__func = func
        
        self.__have_reply.acquire()                             # wait until gui action is done
        
        if isinstance(self.__reply, Exception):                 # if an exception was caught, re-raise it
            raise self.__reply
        
        return self.__reply                                     # normal reply

    def do_func(self, func, *params):
        ''' !!! Internal use only !!!
            Runs the given function in the GUI thread if necessary.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if func is None or not callable(func):
            raise Exception("Given function to execute is not something callable.")
            
        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(func, *params )
        else:
            return func(*params)

    def ask(self, message:str, default_value:str="" )->str:
        ''' Asks user feedback using a text field.
            User can press cancel, which will raise an exception.
            The given text is returned.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(self.ask, message, default_value )

        result = None 
        
        dlg = wx.TextEntryDialog( None, message, 'HappyScript', default_value )
        if dlg.ShowModal() == wx.ID_OK:
            result = dlg.GetValue()
        dlg.Destroy()
        
        if result is None:
            raise ScriptUserAbortException( "User did not provide value in dialog" )
        
        return result
    
    def ask_number(self, message:str, default_value:int=None )->int:
        ''' Ask user feedback using a numeric field.
            User can press cancel, which will raise an exception.
            The given number is returned.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(self.ask_number, message, default_value )

        result = None 
        if default_value is None:
            default_value = ""
        else:
            default_value = "%d" % default_value
        
        dlg = wx.TextEntryDialog( None, message, 'HappyScript', default_value )
        
        while result is None:
            if dlg.ShowModal() == wx.ID_OK:
                txt_result = dlg.GetValue().encode("latin1")
            else:
                break
            
            try:
                result = int(txt_result)
            except:
                result = None
            
        dlg.Destroy()
        
        if result is None:
            raise ScriptUserAbortException( "User did not provide value in dialog" )
        
        return result

    def ask_yesno(self, message:str, cancel:bool = False) -> bool:
        ''' Ask for user feedback using a yes/no question.
            Cancel button is optional.  It will raise an exception.
            Returns True for 'yes', False for 'no'.
        '''     
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(self.ask_yesno, message, cancel )

        style = wx.YES_NO|wx.CANCEL if cancel else wx.YES_NO  
        dlg = wx.MessageDialog(None, message, 'HappyScript', style=style)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            return True
        elif result == wx.ID_NO:
            return False
        
        raise ScriptUserAbortException( "User did not answer yes/no dialog" )
        
    def ask_image(self, message:str, filename:str, arrow_pos=None, yesno=False, cancel=False, numeric=False):
        ''' Ask user feedback while showing a picture.
            Feedback could be a text, numeric value or yes/no.
            An arrow can be drawn on the image to point the user to something.
            The entire dialog and the image is automatically scaled to fit the screen.  No need to
            make the image in a certain resolution.
            A cancel button may be shown.  When pressed, an exception will be raised.
            
            @param message   Message for user.  Use \n to make a multi-line message.
            @param filename  Path to filename of image to show.  JPG, PNG, GIF, BMP are supported.
            @param arrow_pos  Tuple containing pixel-coordinates for the array to point to.  None
                              if no arrow must be shown.
            @param yesno      Set True if it must be just a yes/no value
            @param cancel     Set True if a cancel button must be shown
            @param numeric    Set True if the value entered must be numeric
            
            @return    For yes/no : True if 'yes' is pressed, otherwise False
                       For text field : string value of text field
                       For numeric : floating point value
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(self.ask_image, message, filename, arrow_pos, yesno, cancel, numeric )
        
        form = FormAskImage(message, filename, arrow_pos, yesno, cancel, numeric )
         
        if form.ShowModal() == wx.ID_CANCEL:
            form.Destroy()
            raise ScriptUserAbortException( "User pressed cancel in dialog" )
         
        result = form.result
        form.Destroy()

        return result
        
    def ask_choice(self, message:str, choices:list, do_assert:bool = True)->int:
        ''' Ask user to select option from a list
            
            @param message   Message for user.  Use \n to make a multi-line message.
            @param choices   List of strings to choose from
            @param do_assert Upon cancel, throw an assertion.  Otherwise returns -1.
            
            @return    Number of selected choice (first=0), or -1 upon cancel
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName()=="ScriptThread":
            return self.__run_with_timer(self.ask_choice, message, choices )
        
        form = FormAskChoice(message, choices )
        
        if form.ShowModal() == wx.ID_CANCEL:
            if do_assert:
                form.Destroy()
                raise ScriptUserAbortException( "User pressed cancel in dialog" )
            
        result = form.result
        form.Destroy()
        
        return result
        
    def ask_open_file(self, message, wildcard):
        ''' Ask user to select a file with a filedialog

            @param message  Message for user. Use \n to make a multi-line message.
            @param wildcard Wildcard for file dialog, to select a specific type of file (e.g .zip files)

            @return     Pathname to the file selected, or None if cancelled
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.ask_open_file, message, wildcard)

        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dlg = wx.FileDialog(
            None, message, wildcard=wildcard, style=style)

        if dlg.ShowModal() == wx.ID_CANCEL:
            return None

        return dlg.GetPath()

    def show_stop_dialog(self, message=None ):
        ''' Shows a non-modal form that stays on top.
            It contains a button to stop the actively running script(s).
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"
            
        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.show_stop_dialog, message)
        
        if message is None:
            message = "Press the 'Stop' button to stop the test."
        
        if self.m_stop_dialog is None:
            self.m_stop_dialog = FormStop(message, self._mngr)
        else:
            self.m_stop_dialog.update_message(message)
        self.m_stop_dialog.Show()

    def close_stop_dialog(self):
        ''' Closes the stop dialog, if any.
            Is always called automatically when a script ends.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if self.m_stop_dialog is None:
            return

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.close_stop_dialog)

        self.m_stop_dialog.Destroy()
        self.m_stop_dialog = None

    def add_scatter_chart(self, name) -> ScatterChart:
        ''' Adds a scatter chart to the main dialog.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.add_scatter_chart, name)

        return self._mngr.charts.add_scatter_chart(name)

    def add_time_chart(self, name) -> TimeChart:
        ''' Adds a time chart to the main dialog.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.add_time_chart, name)

        return self._mngr.charts.add_time_chart(name)

    def add_histogram(self, name:str, binsize:float) -> HistogramChart:
        ''' Adds a histogram chart to the main dialog.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.add_histogram, name, binsize)

        return self._mngr.charts.add_histogram(name, binsize)

    def add_matplotlib(self, name:str) -> MatPlotLibChart:
        ''' Adds a matplotlib chart
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.add_matplotlib, name)

        return self._mngr.charts.add_matplotlib(name)

        
    def get_chart(self, name:str) -> Chart:
        ''' Returns an object representing a previously defined chart.
            @return   chart object, or None if given chart was not yet defined.
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        return self._mngr.charts.get_chart(name)
    
    def delete_chart(self, name:str):
        ''' Deletes the chart with the give name
        '''
        assert not threading.currentThread().getName().startswith("Parallel"), "GUI functions cannot be called from a parallel thread"

        if threading.currentThread().getName() == "ScriptThread":
            return self.__run_with_timer(self.delete_chart, name)

        self._mngr.charts.delete_chart(name)

