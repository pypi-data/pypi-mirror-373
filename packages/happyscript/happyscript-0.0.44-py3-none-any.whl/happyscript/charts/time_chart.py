#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to hold a chart shown on a panel_chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
#
import time

from .time_series import TimeSeries
from .chart import Chart

class TimeChart(Chart):
        
    start_time = None

    def add_series(self, name:str) -> TimeSeries:
        return super().add_series(name)

    def do_add_series(self, name:str) -> TimeSeries:
        ''' Create a new series for this chart.
            Base class will add it to the list of series
        '''
        if self.start_time is None:
            self.start_time = time.time()
        return TimeSeries(self, name, self.get_series_color(), self.start_time)
    
    def get_data_as_text(self)->str:
        ''' Returns the data of all series as text.
        '''
        lines = ""                                          # the resulting text
        all_data = list()                                   # the data for each series
        data_lengths = list()                               # length of data for each series
        next_t = list()                                    # next time to take when printing out lines
        data_pos = list()
        
        line = "time\t"                                     # line with titles, first column is time
        for (k,v) in self._series.items():                  # go over all the series
            line += k + "\t"                                 # add title for the series
            data = v.get_points()                           # get all the X/Y data of the series
            all_data.append(data)
            data_lengths.append(len(data))                  # keep a list of the length of all series
            data_pos.append(0)
            next_t.append(None)
        lines += line.strip() + "\r\n"
            
        num_series = len(data_lengths)
        max_lines = sum(data_lengths)                       # we have at most a line for each data point
        
        for j in range(num_series):                         # get the first timestamp of each series
            if data_lengths[j]>0:
                next_t[j] = all_data[j][0][0]
        
        for _ in range(max_lines):                          # iterate over data, with infinite loop protection
            
            try:
                t = min(x for x in next_t if x is not None) # earliest timestamp of all series
            except:                                         
                break                                       # end of data reached
            
            line = "%f" % t                                 # time in first column
            for j in range(num_series):                     # go over all the series
                
                if next_t[j] is None:                       # no more points in time for this series
                    line += "\t"
                    continue
                    
                if next_t[j] <= t+0.0001:                   # next point reached for this series
                    pos = data_pos[j]
                    line += "\t" + str(all_data[j][pos][1]) # add value for this series (in second column)
                                
                    pos += 1
                    if pos<data_lengths[j]:                 # more data for this series
                        data_pos[j] = pos                   # increment pointer to next data
                        next_t[j] = all_data[j][pos][0]     # get time of next datapoint
                    else:
                        next_t[j] = None                    # use None to indicate end of data for this series
                        
                else:                                       # next point for this series not yet reached
                    line += "\t"
                    
            lines += line.strip() + "\r\n"
             
        return lines

    def add_values(self, t=None, **values):
        ''' Add values to different series at once that are on this chart.
        
            @param  t        optional, timestamp to use
            @param  values   values to set, using named parameters to specify the series name
        '''
        if t is None:
            t = time.time()                                 # if no time given, use current time
        
        for name, value in values.items():                  # go over all the data points
            series = self.get_series(name)                  # find series for this datapoint
            if series is not None:
                series.add_value(value, t)                  # add value, using same timestamp


