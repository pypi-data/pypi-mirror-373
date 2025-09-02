
class UserPanelValue():
    def __init__(self, value_source, on_set=None, on_update=None):
        """initialiser method
        SmartInput objects are used to keep track of GUI input values

        Arguments:
            value_source -- GUI object to retreive self.value from

        Keyword Arguments:
            on_set -- callback to be run after self.set(), receives self.value as its first argument (default: {None})
        """
        self.__value_source = value_source
        self.__on_set = on_set
        self.__on_update = on_update

    def do_set(self, value=None):
        """ Event handler for the 'set' button.
            Can also be use to set the value and trigger the on_set callback.
        """
        if value is None:           # no value given -> take value from GUI object
            value = self.value
        else:                       # value given -> set it to GUI object
            self.value = value

        if self.__on_set is not None:
            self.__on_set(value)
    
    @property
    def value(self):
        ''' Gets the value of the GUI object.
        '''
        return self.__value_source.GetValue()
    
    @value.setter
    def value(self, value):
        ''' Sets the value of the GUI object immediately.
            If an 'update' method is defined, it will be called.
        '''
        self.__value_source.SetValue(value)
        self.update()


    def update(self):
        ''' Calls the 'on_update' method if it was defined.
            This is typically used to update a label related to the GUI object.
        '''
        if self.__on_update is not None:
            value = self.__value_source.GetValue()
            self.__on_update(value)
