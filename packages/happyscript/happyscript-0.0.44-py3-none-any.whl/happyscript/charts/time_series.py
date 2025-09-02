#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Series for a chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
# A data series to show on a chart
#
import time
import wx
from wx.lib import plot as wxplot


class TimeSeries(object):

    def __init__(self, chart, name, color, start_time=None):
        '''
        Constructor
        '''
        self.__chart = chart
        self.__name = name
        self.__points = list()
        self.__color = color
        self.__start_time = time.time() if start_time is None else start_time
        
    @property
    def name(self):
        return self.__name
        
    def get_plot_object(self):
        ''' !!! Internal use only !!!
            Gets the object to draw on the chart.
        '''
        line = wxplot.PolyLine(self.__points, colour=self.__color, width=2, style=wx.PENSTYLE_SOLID, legend=self.name)
        
        return line
    
    def add_value(self, value:float, t:float=None):
        ''' Add a value for a time chart.
            Time is by default the actual time.  Any time as returned by time.time() can be used.
            The start time of creating the chart is subtracted from the time.
        '''
        if t is None:
            t = time.time()
            
        self.__points.append( (t-self.__start_time, value) )
        self.__chart.update()
        
    def add_values(self, value_time_list:list):
        ''' Add a list of data points (for a time series graph)
            timevalue_time_list_value_points must be a list of tuples with value as first element
            and time as second element.
            As with add_value, the start time of creating the chart is subtracted from the time.
        '''
        assert isinstance(value_time_list, list), "time_value_points must be a list of time-value tuples"
        if len(value_time_list) == 0:
            return
        assert isinstance(value_time_list[0], tuple), "time_value_points must be a list of time-value tuples"

        for value, t in value_time_list:
            self.__points.append( (t-self.__start_time, value) )
        self.__chart.update()


    def clear(self):
        ''' Clear the data points.
        '''
        self.__points = list()
        self.__chart.update()
        
    def get_points(self):
        ''' Returns all the data points.
        '''
        return self.__points
    