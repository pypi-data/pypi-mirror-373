#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to hold a chart shown on a panel_chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
#
#  https://medium.com/@maxmarkovvision/optimal-number-of-bins-for-histograms-3d7c48086fde

from .histogram_series import HistogramSeries
from .chart import Chart

class HistogramChart(Chart):
        
    def __init__(self, parent_control, name, binsize):
                
        super().__init__(parent_control, name)
        self.__binsize = binsize
        
        self._xlabel = "Value"
        self._ylabel = "Count"

    def add_series(self, name:str) -> HistogramSeries:
        return super().add_series(name)

    def do_add_series(self, name:str) -> HistogramSeries:
        ''' Create a new series for this chart.
            Base class will add it to the list of series
        '''
        return HistogramSeries(self, name, self.__binsize, color=self.get_series_color() )
    
    def get_data_as_text(self) -> str:
        ''' Returns the data of all series as text.
        '''
        lines = ""                                          # the resulting text
        data = list()                                   # the data for each series
        min_x = None
        max_x = None
        
        line = "Value"                                      # add line with all the names
        for ser in self._series:
            line += "\t" + ser
        lines += line.strip() + "\r\n"
        
        for ser in self._series.values():                   # get data and min/max of all series
            points = ser.get_points()
            if min_x is None:
                min_x = min(points.keys())
            else:
                min_x = min( min_x, min(points.keys()))
                
            if max_x is None:
                max_x = max(points.keys())
            else:
                max_x = max( max_x, max(points.keys()))
                
            data.append( points )
            
        for x in range(min_x,max_x+1):                      # write out all the data points
            
            line = str( x * self.__binsize )
            for pts in data:
                if x in pts:
                    line += "\t%d" % pts[x]
                else:
                    line += "\t0"
            lines += line.strip() + "\r\n"
             
        return lines
