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


class HistogramSeries(object):

    def __init__(self, chart, name, binsize, color):
        '''
        Constructor
        '''
        self.__chart = chart
        self.__name = name
        self.__points = dict()
        self.__binsize = binsize
        self.__color = color
        
    @property
    def name(self):
        return self.__name
        
    def get_plot_object(self):
        ''' !!! Internal use only !!!
            Gets the object to draw on the chart.
        '''
        bs = self.__binsize                                         # shorthand
        data = list()                                               # list with all points for the plot

#         prev = 0.5
#         for k in sorted(self.__points.keys()):                      # go over all points by key value
#             
#             if k != prev+1:                                         # if gap between previous point
#                 data.append( ((prev+1)*bs,0) )                      # add a 0 after previous point
#                 if k != prev+2:
#                     data.append( ((k-1)*bs,0) )                     # and also before new point if gap > 2
#             data.append( (k * bs, self.__points[k]) )               # add data point
#             prev = k
#         data.append( ((prev+1)*bs,0) )                              # add final 0 after last point
# 
#         line = wxplot.PolySpline(data, colour=self.__color, width=2, style=wx.PENSTYLE_SOLID, legend=self.name)

        prev = None
        prev_val = None
        for k in sorted(self.__points.keys()):                      # go over all points by key value
            
            if prev is None:                                        # start at 0 for first point
                data.append( (k*bs,0) ) 
                data.append( (k*bs, self.__points[k]) )           # add data point on left
            elif k != prev+1:                                       # if gap between previous point
                data.append( ((prev+1)*bs,0) )                          # add a 0 after previous point
                data.append( (k*bs,0) )                             # this series starts at 0
                data.append( (k*bs, self.__points[k]) )           # add data point on left
            else:                                                   # no gap
                if prev_val != self.__points[k]:                    # new value is different
                    data.append( (k*bs, self.__points[k]) )       # add data point on left
            
            data.append( ((k+1) * bs, self.__points[k]) )           # add data point on right

            prev_val = self.__points[k]
            prev = k
            
        data.append( ((prev+1)*bs,0) )                              # add final 0 after last point

        line = wxplot.PolyLine(data, colour=self.__color, width=2, style=wx.PENSTYLE_SOLID, legend=self.name)

        return line
    
    def add_value(self, x:float):
        ''' Add a value
        '''
        
        binnum = int( x / self.__binsize )
#         if binnum>0 and binnum<100:
#             self.__points[binnum] = self.__points[binnum] + 1
        if binnum in self.__points:
            self.__points[binnum] = self.__points[binnum] + 1
        else:
            self.__points[binnum] = 1

        self.__chart.update()

    def add_values(self, data:list[float]):
        ''' Add all the values from a list.
        '''
        
        for x in data:
            binnum = int( x / self.__binsize )
            if binnum in self.__points:
                self.__points[binnum] = self.__points[binnum] + 1
            else:
                self.__points[binnum] = 1

        self.__chart.update()
        
    def clear(self):
        ''' Clear the data points.
        '''
        self.__points = [0 for _ in range(100)]
        self.__chart.update()
        
    def get_points(self):
        ''' Returns all the data points.
        '''
        return self.__points
    