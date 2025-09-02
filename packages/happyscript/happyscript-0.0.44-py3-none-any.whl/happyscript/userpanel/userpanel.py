import wx
import wx.xrc
from .userpanelvalue import UserPanelValue
import time

class UserPanel(wx.Panel):
    """
    Public methods
    """

    def __init__(self, parent):
        """GUI builder for widgets to be used with happyscript

        Keyword Arguments:
            parent -- The window parent. This may be, and often is, None.
        """
        wx.Panel.__init__(self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, style = wx.TAB_TRAVERSAL, name = wx.EmptyString )
        self.__mainbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__mainbox)
        self.Layout()

        self.__current_top_box = None                       # StaticBoxSizer with label to group controls
        self.__timers=[]
        self.Bind(wx.EVT_CLOSE, self.__on_close)                # for stopping all the timers


    def add_box(self, title:str) -> None:
        """adds a box with a title to be used to contain the widgets

        Arguments:
            title: label for the box
        """
        self.__current_top_box = wx.StaticBoxSizer(wx.StaticBox(self, label=title), wx.VERTICAL)
        self.__mainbox.Add(self.__current_top_box, 0, wx.EXPAND, 5)

    def add_buttons(self, label, event, button_labels : list[str]) -> None:
        """adds a horizontal row of buttons, which trigger the button_event(button_label) callback)

        Arguments:
            label: label to be placed left of the buttons, or None to have no label
            event: callback triggered on button presses
            button_labels -- list of labels (one for each button)
        """
        self.__current_sub_box = self.__create_boxsizer()
        if label is not None:
            self.__insert_label(label, 1)
        for button_label in button_labels:
            event_wrapper = lambda *args, x=button_label: event(x)
            proportion = 1 if (label is None) else 0
            self.__insert_button(button_label, event_wrapper, proportion)

    def add_slider(self, label:str, event, value:int, min_val:int, max_val:int) -> UserPanelValue:
        """ Adds a slider for the user to set a value.
        event function is called when the 'set' button is pressed, with the slider value as parameter

        Arguments:
            label: label to be placed left of the slider
            event: callback triggered when pressing the 'set' button
            value: slider initial value
            min_val: slider minimum value
            max_val: slider maximum value 

        Returns: object to access the slider value
        """
        self.__current_sub_box= self.__create_boxsizer()
        self.__insert_label(label)
        slider_obj = self.__insert_slider(value, min_val, max_val, 1)
        label_obj = self.__insert_label(str(value))
        smart_input = UserPanelValue(slider_obj,
                                     on_set=event,
                                     on_update=lambda *args: label_obj.SetLabel(str(slider_obj.GetValue())) )
        self.__insert_button("Set", lambda *args: smart_input.do_set(), 0)
        slider_obj.Bind(wx.EVT_SLIDER, lambda *args: smart_input.update())
        return smart_input

    def add_combo_box(self, label:str, event, choices : list[str]) -> UserPanelValue:
        """ Adds a combo box for the user to set a value.
        event function is called when the 'set' button is pressed, with the combo box value as parameter

        Arguments:
            label: label to be placed left of the combo box
            event: callback triggered when pressing the 'set' button
            choices: list of options to be presented in the combo box

        Returns: object to access the combo box value
        """
        self.__current_sub_box = self.__create_boxsizer()
        self.__insert_label(label)
        combo_obj = self.__insert_combo_box(choices, 1)
        smart_input = UserPanelValue(combo_obj, event)
        self.__insert_button("Set", lambda *args: smart_input.do_set(), 0)
        return smart_input

    def add_spin_control(self, label:str, event, value:int, min_val:int, max_val:int):
        """  Adds a spin control for the user to set a value.
        event function is called when the 'set' button is pressed, with the spin control value as parameter.

        Arguments:
            label: label to be placed left of the spin control
            event: callback triggered when pressing the 'set' button
            value: spin control initial value
            min_val: spin control minimum value
            max_val: spin control maximum value

        Returns: object to access the spin control value
        """
        self.__current_sub_box = self.__create_boxsizer()
        self.__insert_label(label)
        spin_obj = self.__insert_spin_control(value, min_val, max_val, 1)
        smart_input = UserPanelValue(spin_obj, event)
        self.__insert_button("Set", lambda *args: smart_input.do_set(), 0)
        return smart_input

    def add_timer_control(self, label, event, interval_s):
        """ allows the user to periodically trigger a callback
            the timer interval is set with a spin control, in seconds
            pressing start or stop will (re)start or stop the interval timer

        Arguments:
            label -- label to be placed on the left
            event -- callback to be triggered each interval
            interval_s -- interval default value
        """
        #        Timer info: https://www.blog.pythonlibrary.org/2009/08/25/wxpython-using-wx-timers/
        self.__current_sub_box = self.__create_boxsizer()
        self.__insert_label(label, 1)
        spin_obj = self.__insert_spin_control(interval_s, 1, 86400, 1)
        self.__insert_label("s")

        new_timer = wx.Timer(spin_obj)
        spin_obj.Bind(wx.EVT_TIMER, lambda ev: event(), new_timer)
        self.__timers.append(new_timer)
        self.__insert_button("Start", lambda *args: new_timer.Start(1000 * spin_obj.GetValue()), 0)
        self.__insert_button("Stop", lambda *args: new_timer.Stop(), 0)

    """
    private methods
    """

    def __create_boxsizer(self, orientation=wx.HORIZONTAL, proportion=0):
        """setup for a BoxSizer
        """
        if self.__current_top_box is None:
            self.add_box("Miscellaneous")
        box = wx.BoxSizer(orientation)
        self.__current_top_box.Add(box, proportion, wx.EXPAND, 5)
        return box

    def __insert_label(self, label_text, proportion=0):
        """setup for a label
        """
        label = wx.StaticText(self.__current_top_box.GetStaticBox(), label=label_text)
        label.Wrap(-1)
        self.__current_sub_box.Add(label, proportion, wx.ALL, 5)
        return label

    def __insert_button(self, button_label, button_event, proportion):
        """setup for a button
        """
        button = wx.Button(self.__current_top_box.GetStaticBox(), label=button_label)
        button.Bind(wx.EVT_BUTTON, button_event)
        self.__current_sub_box.Add(button, proportion, wx.ALL, 5)
        return button

    def __insert_slider(self, initial, min, max, proportion):
        """setup for a slider
        """
        slider = wx.Slider(self.__current_top_box.GetStaticBox(), value=initial, minValue=min, maxValue=max)
        self.__current_sub_box.Add(slider, proportion, wx.ALL | wx.EXPAND, 5)
        return slider

    def __insert_combo_box(self, option_list, proportion):
        """setup for a combo box
        """
        combo = wx.ComboBox(self.__current_top_box.GetStaticBox(), value=option_list[0], choices=option_list)
        self.__current_sub_box.Add(combo, proportion, wx.ALL, 5)
        return combo

    def __insert_spin_control(self, initial, min, max, proportion):
        """setup for a spin control
        """
        spin = wx.SpinCtrl(self.__current_top_box.GetStaticBox(), initial=initial, min=min, max=max)
        self.__current_sub_box.Add(spin, proportion, wx.ALL, 5)
        return spin
    
    def __on_close(self, wxEvent):
        """cancels the running timer threads
        """
        for timer in self.__timers:
            timer.Stop()
        self.Destroy()