#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Series for a chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
# A data series to show on a chart
#

import wx
from wx.lib import plot as wxplot


class ScatterSeries(object):

    def __init__(self, chart, name, color):
        '''
        Constructor
        '''
        self.__chart = chart
        self.__name = name
        self.__points = list()
        self.__color = color
        
    @property
    def name(self):
        return self.__name
        
    def get_plot_object(self):
        ''' !!! Internal use only !!!
            Gets the object to draw on the chart.
        '''
        line = wxplot.PolyLine(self.__points, colour=self.__color, width=2, style=wx.PENSTYLE_SOLID, legend=self.name)
        
        return line
    
    def add_point(self, x:float, y:float):
        ''' Add a data point (for a scatter graph)
        '''
        self.__points.append( (x, y) )
        self.__chart.update()
        
    def add_points(self, xypoints:list):
        ''' Add a list of data points (for a scatter graph)
            xypoints must be a list of tuples (x, y)
        '''
        assert isinstance(xypoints, list), "xypoints must be a list of xvalue-yvalue tuples"
        if len(xypoints) == 0:
            return
        assert isinstance(xypoints[0], tuple), "xypoints must be a list of xvalue-yvalue tuples"

        self.__points.extend(xypoints)
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
    