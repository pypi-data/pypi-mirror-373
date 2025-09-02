
import wx
import os
import logging

from ..panels.panelsbase import PanelCharts_Base
from ..charts.scatter_chart import ScatterChart
from ..charts.time_chart import TimeChart
from ..charts.histogram_chart import HistogramChart
from ..charts.matplotlib_chart import MatPlotLibChart

# old_pages = dict()

class PanelCharts( PanelCharts_Base):
    ''' Panel containing one or more plots
    '''

    def __init__( self, parent):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param dirname  Directory name to reads scripts from.
        '''
        super().__init__(parent)
        self.__dirty = False
        self.charts = dict()
        self.default_savedir = os.getcwd()

    def update(self):
        ''' Triggers update of chart.
            The chart is not updated immediately, but using a 50ms timer.
            Note that we don't use a one-shot timer because that cannot be started from another thread.
        '''
        self.__dirty = True
        
    def OnRedrawTimer( self, event ):
        ''' Charts are redrawn using a timer when necessary.
            This way, high-frequency updates of the chart will only be shown at a moderate rate.
            @TODO:   Update only visible chart
        '''
        if self.__dirty:
            self.__dirty = False
            for x in self.charts.values():
                x.redraw()

    def OnRadioBoxMouseMode( self, event ):
        
        for chart in self.charts.values():
            if self.m_rbxMouseMode.Selection==0:
                chart.enableZoom = False
                chart.enableDrag = False
            elif self.m_rbxMouseMode.Selection==1:
                chart.enableZoom = True
                chart.enableDrag = False
            else:
                chart.enableDrag = True
                chart.enableZoom = False

    def BtnCopyDataClick( self, event ):
        index = self.m_nbkPlots.GetSelection()
        if index == wx.NOT_FOUND or self.m_nbkPlots.GetPageText(index) not in self.charts:
            wx.MessageBox( "Cannot find chart on current page", "HappyScript", wx.OK | wx.ICON_ERROR )

        chart = self.charts[self.m_nbkPlots.GetPageText(index)]     # get chart on current page
        
        try:
            clipdata = wx.TextDataObject()
            lines = chart.get_data_as_text()
            clipdata.SetText(lines)
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()
            wx.MessageBox( "Data written to clipboard", "HappyScript", wx.OK | wx.ICON_INFORMATION )
        except:
            wx.MessageBox( "Could not write text to clipboard", "HappyScript", wx.OK | wx.ICON_ERROR )
        
    def OnMakePretty( self, event ):
        index = self.m_nbkPlots.GetSelection()
        if index == wx.NOT_FOUND or self.m_nbkPlots.GetPageText(index) not in self.charts:
            wx.MessageBox( "Cannot find chart on current page", "HappyScript", wx.OK | wx.ICON_ERROR )

        chart = self.charts[self.m_nbkPlots.GetPageText(index)]     # get chart on current page

        chart.update(antialiasing = True)
        
        
    def OnBtnSaveBitmap( self, event ):
        index = self.m_nbkPlots.GetSelection()
        if index == wx.NOT_FOUND or self.m_nbkPlots.GetPageText(index) not in self.charts:
            wx.MessageBox( "Cannot find chart on current page", "HappyScript", wx.OK | wx.ICON_ERROR )

        chart = self.charts[self.m_nbkPlots.GetPageText(index)]     # get chart on current page
        
        try:
            with wx.FileDialog(self, "Output file name", wildcard="PNG files(*.png)|*.png",
                    defaultDir = self.default_savedir,
                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fdlg:

                if fdlg.ShowModal() == wx.ID_OK:
                    filename = fdlg.GetPath()
                    chart.SaveFile(filename)
                    self.default_savedir = os.path.dirname(filename)
        except:
            wx.MessageBox( "Could not write bitmap", "HappyScript", wx.OK | wx.ICON_ERROR )
        
    def get_chart(self, name):
        ''' Returns chart object with the given name, or None if chart does not exist.
        '''
        if name in self.charts:
            return self.charts[name]
        else:
            return None

    def delete_chart(self, name):
        ''' Deletes the chart with the given name
        '''
        if not name in self.charts:
            return 
        
        ch = self.charts[name]
        page_num = self.m_nbkPlots.FindPage(ch)
        
        if page_num != wx.NOT_FOUND:
            self.m_nbkPlots.DeletePage(page_num)
            # page_num.Hide()
        
        # self.charts[name].clear()
        del self.charts[name]
        
    def add_scatter_chart(self, name ):
        ''' Creates a new chart with the given options.
        '''
        self.delete_chart(name)                                             # delete chart if it would already exist
            
        chart = ScatterChart(self.m_nbkPlots, name)                # create new chart and remember it
        chart.on_update = self.update
        self.charts[name] = chart
        
#         self.m_nbkPlots.AddPage( chart.plotcanvas, name, True)                      # chart to dialog
        self.m_nbkPlots.AddPage( chart, name, True)                      # chart to dialog
        return chart
        
    def add_time_chart(self, name ):
        ''' Creates a new time chart with the given options.
        '''
        self.delete_chart(name)                                             # delete chart if it would already exist
            
        chart = TimeChart(self.m_nbkPlots, name)                # create new chart and remember it
        chart.on_update = self.update
        self.charts[name] = chart
        
        self.m_nbkPlots.AddPage( chart, name, True)                      # chart to dialog
        return chart

    def add_histogram(self, name, binsize ):
        ''' Creates a new histogram chart with the given options.
        '''
        self.delete_chart(name)                                             # delete chart if it would already exist
            
        chart = HistogramChart(self.m_nbkPlots, name, binsize)              # create new chart and remember it
        chart.on_update = self.update
        self.charts[name] = chart
        
        self.m_nbkPlots.AddPage( chart, name, True)                      # chart to dialog
        return chart
        
    def add_matplotlib(self, name ):
        ''' Creates a new matplotlib chart
        '''
        self.delete_chart(name)                                             # delete chart if it would already exist
            
        # if name in old_pages:
        #     nbk = old_pages[name]
        #     nbk.Show()
        # else:
        chart = MatPlotLibChart(self.m_nbkPlots, name)                # create new chart and remember it
            # old_pages[name] = chart
        # chart = MatPlotLibChart.create(self.m_nbkPlots, name)                # create new chart and remember it
        
        assert chart.figure is not None, "Could not add matplotlib chart."
        
        chart.on_update = self.update
        self.charts[name] = chart
    
        self.m_nbkPlots.AddPage( chart, name, True)                      # chart to dialog
            # old_pages[name] = nbk
            
        return chart

        
#stop-amalgamation

class PlotDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        self.m_thePanel = PanelCharts(self)
        bSizer21.Add( self.m_thePanel, 1, wx.EXPAND |wx.ALL, 5 )

        self.SetSizer( bSizer21 )


        #--------------------------------------------------------------- add python Shell
        scriptLocals = { "panel": self.m_thePanel, "plot": self.m_thePanel.plot1 }
        self._shell_window = wx.py.shell.Shell( self, -1, introText = None, locals=scriptLocals )
        
        bSizer21.Add(self._shell_window, 1, wx.EXPAND |wx.ALL, 5)

#         info = wx.aui.AuiPaneInfo().Caption("Python shell").Name("PY_Shell")
#         info.Bottom().Layer(1).Dock().CloseButton(False)
# 
#         self.m_mgr.AddPane(self._shell_window, info)



        self.Layout()
        self.Centre( wx.BOTH )

        self.Bind( wx.EVT_CLOSE, self.OnClose )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnClose( self, event ):
        self.Destroy()

if __name__=="__main__":
    
    app = wx.App()
    
    form = PlotDialog(None)
    
    form.ShowModal()
    
    app.MainLoop()

    
