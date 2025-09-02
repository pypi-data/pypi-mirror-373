#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to hold a chart shown on a panel_chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
#

import wx
from wx.lib import plot as wxplot

class Chart(wxplot.PlotCanvas):
    ''' Base object for all charts.
        Derived chart has to implement :
        * do_redraw (optionally)
        * do_add_series
        * get_data_as_text
    '''

    COLORS = ( wx.Colour(68,114,196), wx.Colour(237,125,49), wx.Colour(165,165,165), wx.Colour(255,193,4),
               wx.Colour(91,155,213), wx.Colour(112,173,71), wx.Colour(38,68,120), wx.Colour(158,72,14),
               wx.Colour(99,99,99),  wx.Colour(153,115,0), wx.Colour(37,94,145), wx.Colour(67,104,43),
               wx.Colour(105,142,208),  wx.Colour(241,151,90), wx.Colour(183,183,183), wx.Colour(255,205,51),
               wx.Colour(124,175,221),
               )
    

    def __init__(self, parent_control, name):
        '''
        Constructor
        '''
        super().__init__(parent_control, -1)
        
        self.__name = name
        
        self.enableLegend = True
        self.enableGrid = True
        self.antiAlias = False
        
        self._series = dict()
        self.__dirty = False
        self.__on_update_func = None
        self.__num_series_added = 0                 # count num of series added, to select next color

        self._xrange = None
        self._yrange = None
        self.configure(title=name, x_label="", y_label="", x_log=False, y_log=False)

    def get_series_color(self):
        ''' Get next color to use for a newly added series.
        '''
        idx = self.__num_series_added % len(self.COLORS)
        self.__num_series_added += 1
        return self.COLORS[idx]
        
    @property
    def name(self):
        return self.__name
    
    def configure(self, /, x_label=None, y_label=None, title=None,
                  y_log=None, x_log=None, x_range=None, y_range=None):
        '''
            
        '''
        if title is not None:
            self._title = title if isinstance(title, str) else str(title)
            self.enablePlotTitle = True if len(self._title)>0 else False
        if x_label is not None:
            self._xlabel = x_label if isinstance(x_label, str) else str(x_label)
            self.enableXAxisLabel = True if len(self._xlabel)>0 else False
        if y_label is not None:
            self._ylabel = y_label if isinstance(y_label, str) else str(y_label)
            self.enableYAxisLabel = True if len(self._ylabel)>0 else False
        if x_log is not None:
            self._xlog = True if x_log else False
        if y_log is not None:
            self._ylog = True if y_log else False
    
        if x_range is not None:
            ok = False
            if type(x_range) is tuple and len(x_range)==2:
                try:
                    if x_range[0]+1 < x_range[1]+1:
                        self._xrange = x_range
                    ok = True
                except:
                    pass
            if not ok:
                print(f"x_range {x_range} is invalid")
    
        if y_range is not None:
            ok = False
            if type(y_range) is tuple and len(y_range)==2:
                try:
                    if y_range[0]+1 < y_range[1]+1:
                        self._yrange = y_range
                    ok = True
                except:
                    pass
            if not ok:
                print(f"y_range {y_range} is invalid")

        self.logScale = (self._xlog, self._ylog)
        if len(self._series)>0:
            self.update()
        
    @property
    def on_update(self):
        ''' The callback function for when data is modified.
        '''
        return self.__on_update_func
    
    @on_update.setter
    def on_update(self, value):
        ''' Set the callback function for when data is modified.
        '''
        if value is None or callable(value):
            self.__on_update_func = value
    
    @property
    def dirty(self):
        ''' Returns if the chart needs updating or not.
        '''
        return self.__dirty
    
    def update(self, / , antialiasing=False):
        ''' Indicate that a chart should be updated. To be executed by a chart series when data is added.
            The internal 'dirty' flag is set.
            Also, the on_update callback function is called (if one is set).

            In a a chart panel, the callback function will set a flag to indicate that the chart must
            be updated.
        ''' 
        self.antiAlias = antialiasing
        self.__dirty = True
        if self.__on_update_func is not None:
            self.__on_update_func()
        
    def redraw(self):
        ''' Redraw the chart.
            Updates of the charts are 'lazy' : they are not recalculated when data is added.
            The GUI calls this function to ask for the chart to be redrawn.
            The internal 'dirty' flag is cleared.
        '''
        self.enableAntiAliasing = self.antiAlias
        self.antiAlias = False
        self.do_redraw()
        # print(f"redraw  {self.enableAntiAliasing}")
        self.__dirty = False
        
        
    def do_redraw(self):
        ''' Is called when the chart must be redrawn.
            Standard implementation below.
            May be overridden for special kinds of charts.
        '''
        plot_objects = list()
        try:
            for series in self._series.values():
                if len(series.get_points())>0:
                    plot_objects.append( series.get_plot_object() )
                
        except RuntimeError:                # occurs sometimes when data is updated during redraw
            return
            
        if len(plot_objects)>0:
            pg = wxplot.PlotGraphics(plot_objects, self._title, self._xlabel, self._ylabel)
            try:
                self.Draw(pg, xAxis=self._xrange, yAxis=self._yrange)
            except:
                pass
        
    # def clear(self):
    #     ''' remove all series from the chart
    #     '''
    #     for name in self._series.keys():
    #         del self._series[name]                                 # delete it
    #         if hasattr(self, name):
    #             delattr(self, name)                                 # delete member variable as well
        
    def delete_series(self, name):
        ''' Remove a series from a chart.
        '''
        if name in self._series:                                   # check if we have a series with that name
            del self._series[name]                                 # delete it
            if hasattr(self, name):
                delattr(self, name)                                 # delete member variable as well
        
    def add_series(self, name):
        ''' Create a new series for this chart.
            First checks if name is valid, then calls do_add_series of derived class to create the series.
            Series is added as attribute to the chart itself.
        '''
        if ( not name.isidentifier() or                             # first check if name is valid
             name in ['update', 'redraw', 'add_series', 'delete_series'] or
             ( hasattr(self, name) and name not in self._series) ):
            raise ValueError("Series name '%s' is invalid" % name)
        
        self.delete_series(name)                                    # delete old series if necessary
        
        series = self.do_add_series(name)                           # create the series and remember it
        
        if series is not None:
            self._series[name] = series
            setattr(self, name, series)                             # also set it as a member variable
            
        self.update()
        return series
    
    def do_add_series(self, name):
        ''' To be implemented by derived class.
        '''
        return None
    
    def get_series(self, name):
        ''' Return a series by name, or None if it doesn't exist
        '''
        if name in self._series:
            return self._series[name]
        else:
            return None
    
    def get_data_as_text(self):
        ''' Returns the data of all series as text.
            TO BE IMPLEMENTED FOR EACH CHART TYPE
            Data must be separated by a tab for easy Excel import
        '''
        return ""
