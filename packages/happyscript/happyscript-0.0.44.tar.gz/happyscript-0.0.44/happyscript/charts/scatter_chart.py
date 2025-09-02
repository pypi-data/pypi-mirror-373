#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to hold a chart shown on a panel_chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
#

from .scatter_series import ScatterSeries
from .chart import Chart

class ScatterChart(Chart):
        
    def add_series(self, name:str) -> ScatterSeries:
        return super().add_series(name)

    def do_add_series(self, name:str) -> ScatterSeries:
        ''' Create a new series for this chart.
            Base class will add it to the list of series
        '''
        return ScatterSeries(self, name, color=self.get_series_color() )
    
    def get_data_as_text(self)->str:
        ''' Returns the data of all series as text.
        '''
        lines = ""                                          # the resulting text
        all_data = list()                                   # the data for each series
        data_lengths = list()                               # length of data for each series
        
        line = ""                                           # line with titles
        for (k,v) in self._series.items():                  # go over all the series
            line += k + "_x\t" + k + "_y\t"                 # add title for X/Y of the series
            data = v.get_points()                           # get all the X/Y data of the series
            all_data.append(data)
            data_lengths.append(len(data))                  # keep a list of the length of all series
        lines += line.strip() + "\r\n"
            
        num_series = len(data_lengths)
        num_lines = max(data_lengths)
        for i in range(num_lines):
            line = ""
            for j in range(num_series):
                if data_lengths[j]>i:
                    line += "\t".join(map(str,all_data[j][i]))+"\t"
                else:
                    line += "\t\t"
            lines += line.strip() + "\r\n"
             
        return lines
