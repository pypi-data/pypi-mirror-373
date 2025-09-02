#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to hold a chart shown on a panel_chart
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : na
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 2/1/2022
#__________________________________________________|_________________________________________________________
#
#
import logging
import wx

try:
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
    from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAVE_MATPLOTLIB = True
except ImportError:
    HAVE_MATPLOTLIB = False

class MatPlotLibChart(wx.Panel):

    def __init__(self, parent_control, name):
        '''
        Constructor
        '''
        super().__init__(parent_control, -1)
        
        self.__name = name
        
        self.__dirty = False
        self.__on_update_func = None
        
        if not HAVE_MATPLOTLIB:
            logging.error("Matplotlib is not installed.")
            self.__figure = None
            return
        
        # if name in fig_canvas_toolbar:
        #     f,c,t = fig_canvas_toolbar[name]
        #     f.clf()
        #     self.__figure = f
        #     self.canvas = c
        #     self.__toolbar = t
        # else:
        self.__figure = Figure(dpi=None, figsize=(2, 2))
        # plt.figure(self.__figure)
        # self.__figure = plt.figure(name, dpi=None, figsize=(2, 2))
            # try:
            #     plt.clf()
            # except:
            #     pass
        self.__figure.set_tight_layout(True)
        self.canvas = FigureCanvas(self, -1, self.__figure)
        self.__toolbar = NavigationToolbar(self.canvas)
        self.__toolbar.Realize()
        # self.__toolbar = None
            
        # fig_canvas_toolbar[name] = (self.__figure, self.canvas, self.__toolbar)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.__toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        
    @property
    def name(self):
        return self.__name
    
    @property
    def figure(self) -> 'Figure':
        return self.__figure
    
    def configure(self, /, x_label=None, y_label=None, title=None,
                  y_log=None, x_log=None, x_range=None, y_range=None):
        '''
        '''
        if not HAVE_MATPLOTLIB: return
        
        if title is not None and isinstance(title, str):
            if len(self.figure.axes)>0:
                self.figure.axes[0].set_title(title)
                self.update()
                    
    @property
    def on_update(self):
        ''' !!! Internal use only !!!!
            The callback function for when data is modified.
        '''
        return self.__on_update_func
    
    @on_update.setter
    def on_update(self, value):
        ''' !!! Internal use only !!!!
            Set the callback function for when data is modified.
        '''
        if value is None or callable(value):
            self.__on_update_func = value
    
    @property
    def dirty(self):
        ''' !!! Internal use only !!!!
            Returns if the chart needs updating or not.
        '''
        return self.__dirty
    
    def update(self, / , antialiasing=False):
        ''' Indicate that a chart should be updated. To be executed by a chart series when data is added.
            The internal 'dirty' flag is set.
            Also, the on_update callback function is called (if one is set).

            In a a chart panel, the callback function will set a flag to indicate that the chart must
            be updated.
        ''' 
        if antialiasing:
            logging.warn("Antialiasing not supported for matplotlib chart")

        self.__dirty = True
        if self.__on_update_func is not None:
            self.__on_update_func()
        
    def redraw(self):
        ''' Redraw the chart.
            Updates of the charts are 'lazy' : they are not recalculated when data is added.
            The GUI calls this function to ask for the chart to be redrawn.
            The internal 'dirty' flag is cleared.
        '''
        # self.enableAntiAliasing = self.antiAlias
        self.antiAlias = False
        self.do_redraw()
        self.__dirty = False
        
    def do_redraw(self):
        ''' !!! Internal use only !!!!
            Is called when the chart must be redrawn.
            Standard implementation below.
            May be overridden for special kinds of charts.
        '''
        if not HAVE_MATPLOTLIB: return
        
        self.canvas.draw()
        
    def clear(self):
        ''' remove all series from the chart
        '''
        if not HAVE_MATPLOTLIB: return

        try:
            self.figure.clf()
        except:
            pass
        # # plt.figure(self.name)
        # # plt.clf()
        # # plt.close()
        pass
        
    def delete_series(self, name):
        logging.error("Deleting series not supported for matplotlib charts")
        
    def add_series(self, name):
        logging.error("Use matplotlib API for adding series")
    
    def get_series(self, name):
        logging.error("Getting series not supported for matplotlib charts")
        return None
    
    def get_data_as_text(self):
        logging.error("Getting series not supported for matplotlib charts")
        return "Data not available for matplotlib charts" 

