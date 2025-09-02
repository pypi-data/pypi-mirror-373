#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Main form for happyscript application
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Varia
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import wx
import wx.py as py
import configparser 

try:
    from agw import aui
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

from ..scriptartwork import ScriptArtwork
from .form_ontestfailure import FormOnTestFailure
from .form_serials import FormSerials
from ..panels.panel_messages import PanelMessages
from ..panels.panel_tests import PanelTests
from ..panels.panel_log import PanelLog
from ..charts.panel_charts import PanelCharts
# from .printredirect import PrintRedirect

#=====================================================================================================================
#   Class FormProduction
#=====================================================================================================================

from .formsbase import FormMain_Base 

class FormMain(FormMain_Base):

    VALID_OPERATORS = ("OPERATOR", "TECHNICIAN", "ENGINEER", "EXPERT")

    def __init__(self, script_manager ):

        ScriptArtwork.register()

        super().__init__(None)

        self.logFile = None
        self._script_manager = script_manager
        self.on_gui_timer = None
        self.on_log_timer = None
        self.current_user = None                        # for which user is the current layout ? 

        #--------------------------------------------------------------- add python Shell
        scriptLocals = { "_mngr_": self._script_manager }
        self._shell_window = py.shell.Shell( self, -1, introText = None, locals=scriptLocals )

        info = wx.aui.AuiPaneInfo().Caption("Python shell").Name("PY_Shell")
        info.Bottom().Layer(1).Dock().CloseButton(False)

        self.m_mgr.AddPane(self._shell_window, info)

        #------------------------------------------------------------- add the custom control panels
        info = wx.aui.AuiPaneInfo().Caption("Control Panels").Name("ControlPanels")
        info.Left().Layer(1).Position(0).CloseButton(False).MinSize( (100,200) )
 
        self._nbk_control_panels = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_mgr.AddPane(self._nbk_control_panels, info)

        #------------------------------------------------------------- add the messages
        info = wx.aui.AuiPaneInfo().Caption("Messages").Name("Messages")
        info.Center().Layer(1).Dock().CloseButton(False).MinSize( (100,200) )
 
        self.msgArea = PanelMessages(self)
        self.m_mgr.AddPane(self.msgArea, info)
        
        #------------------------------------------------------------- add the test list
        info = wx.aui.AuiPaneInfo().Caption("Tests").Name("Tests")
        info.Left().Layer(1).Dock().CloseButton(False).MinSize( (100,200) )
 
        self.pnlTests = PanelTests(self, self._script_manager)
        self.m_mgr.AddPane(self.pnlTests, info)

        #------------------------------------------------------------- add the logging
        info = wx.aui.AuiPaneInfo().Caption("Log").Name("Log")
        info.Bottom().Layer(1).Dock().CloseButton(False).MinSize( (100,200) )
 
        self.logPane = PanelLog(self)
        self.m_mgr.AddPane(self.logPane, info)

        #------------------------------------------------------------- add the charts
        info = wx.aui.AuiPaneInfo().Caption("Charts").Name("Charts")
        info.Bottom().Layer(1).Dock().CloseButton(False).MinSize( (100,200) )
 
        self.chartsPane = PanelCharts(self)
        self.m_mgr.AddPane(self.chartsPane, info)
        
        #-------------------------------------------------------------- add the scripts view
        info = wx.aui.AuiPaneInfo().Caption("Scripts").Name("Scripts")
        info.Right().Layer(1).CloseButton(False).MinSize( (150,150) )

        self._nbk_scripts = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_mgr.AddPane(self._nbk_scripts, info)

        self.ALL_BUTTONS = [self.m_btnTestList, self.m_btnMessages, self.m_btnLogging, self.m_btnPython, self.m_btnScripts, self.m_btnControls, self.m_btnCharts ]
        self.ALL_PANELS  = [self._nbk_scripts, self._nbk_control_panels, self.logPane, self.pnlTests, self.msgArea, self._shell_window, self.chartsPane ]

    def BeforeShow(self):
        ''' Method to be called before the form is first shown.
            The previous user selection and form layout will be restored.
        '''
        self.SwitchUser(None)
        self.m_guiTimer.Start(20)
        
    def OnMnuLayoutClicked( self, event ):
        tb = event.GetEventObject()
        tb.SetToolSticky(event.GetId(), True)
        rect = tb.GetToolRect(event.GetId())
        pt = tb.ClientToScreen(rect.GetBottomLeft())
        pt = self.ScreenToClient(pt)
        self.PopupMenu(self.m_mnuLayout, pt)
        tb.SetToolSticky(event.GetId(), False)
        
    def AddCustomPanel(self, title, panelType, **args):
        ''' Add a custom panel to the pane with control panels.
            The panel constructor MUST have a parameter named 'parent'.  This will be filled in 
            automatically with the object containing the new panel. 
        
            @param  Title        Title for the panel
            @param  panelType    class to instantiate
            @param  args         parameters to supply to the constructor of the class
        '''
        args["parent"] = self._nbk_control_panels
        newPanel = panelType(**args)
        
        self._nbk_control_panels.AddPage( newPanel, title, False)
        return newPanel
        
#         if self.current_user != "OPERATOR":                                     # enable button for showing control panels
#             self.m_mnuToolbar.EnableTool(self.m_btnControls.GetId(), False)

    def HideCustomPanels(self):
        ''' If there are no custom panels in the "ControlPanels" pane, hide that pane.
            This doesn't work properly if the pane has been docked together with another pane.
        '''
        if self._nbk_control_panels.GetPageCount()==0:
            info = self.m_mgr.GetPaneByName("ControlPanels")
            info.Hide()
            self.m_mgr.Update()

    def SwitchUser(self, user):
        ''' Switches the layout to the user "OPERATOR", "TECHNICIAN", "ENGINEER",= or "EXPERT".
            Layout for current user is saved to ini-file, and layout for new user
            is restored from ini-file.
            Different options are enabled/disabled depending on user level.
        '''
        if user is None:                                        # if no user given, take last user from ini-file
            ini = configparser.ConfigParser()
            ini.read( ["happyscript.ini"] )
            user = ini.get("varia", "CurrentUser", fallback="OPERATOR" )
            if user not in self.VALID_OPERATORS:
                user = "OPERATOR"

        if self.current_user == user:                           # no change
            return 
        
        if self.current_user is not None:                       # save layout for present user
            self.SavePosition()
            
        self.current_user = user                                # set new user
        self.RestorePosition()                                  # restore layout of new user
        
        # fixed settings depending on user :
        # - which panels must certainly be hidden
        # - what is the bitmap for the 'user' button
        # - which panel is shown in the center
        # - must buttons be enabled or not ? 

        if self.current_user=="OPERATOR":
            hide_panels = [self.logPane, self._nbk_scripts, self._nbk_control_panels, self._shell_window, self.chartsPane]
            bitmap = ScriptArtwork.GetBitmap("user_operator")
            center = self.msgArea
            enable_buttons = list()
        elif self.current_user=="TECHNICIAN":
            hide_panels = [self._shell_window, self.chartsPane]
            bitmap = ScriptArtwork.GetBitmap("user_technician")
            center = self.logPane        
            enable_buttons = [ self.m_btnControls, self.m_btnScripts, self.m_btnLogging, self.m_btnMessages]
        elif self.current_user=="ENGINEER":
            hide_panels = list()
            bitmap = ScriptArtwork.GetBitmap("user_engineer")
            center = self.logPane            
            enable_buttons = self.ALL_BUTTONS
        else:
            hide_panels = list()
            bitmap = ScriptArtwork.GetBitmap("user_expert")
            center = self._shell_window
            enable_buttons = self.ALL_BUTTONS

        self.m_btnLayout.SetBitmap(bitmap)                      # update icon for user button

        for btn in self.ALL_BUTTONS:                            # enable or disable buttons depending on user
            enable = True if btn in enable_buttons else False
            self.m_mnuToolbar.EnableTool(btn.GetId(), enable )
            
        if center==self.logPane:                                # make sure center panels cannot be hidden
            self.m_mnuToolbar.EnableTool(self.m_btnLogging.GetId(), False)
        elif center==self._shell_window:
            self.m_mnuToolbar.EnableTool(self.m_btnPython.GetId(), False)
            
        pane = self.m_mgr.GetPane(center)                       # which pane is center for this user ?
        pane.Dock().Center()
        if not pane.IsShown():                                  # make sure it is shown and centered
            pane.Show(True)
            
        for panel in [self.msgArea, self.logPane, self._shell_window]:  # make sure no other panels are centered
            if panel == center:
                continue
            pane = self.m_mgr.GetPane(panel)
            if pane.dock_direction == aui.AUI_DOCK_CENTER:
                pane.Dock().Bottom()
                
        if self._nbk_control_panels.PageCount==0:               # disable custom control button if no controls added
            self.m_mnuToolbar.EnableTool(self.m_btnControls.GetId(), False)
            hide_panels.append(self._nbk_control_panels)
        
        for panel in hide_panels:                               # go over all the panels that must be hidden
            pane = self.m_mgr.GetPane(panel)
            if pane.IsShown():                                  # it's visible, so we must hide it
                if pane.IsDocked():                             # undock needed before hiding
                    pane.Float()
                pane.Show(False)                                # hide it
        
        self.m_mnuToolbar.Show()
        self.m_mgr.Update()                                     # tell the manager to 'commit' all the changes just made

    def RestorePosition( self ):
        ''' Restore the position of the window and the panes
        '''
        if self.current_user not in self.VALID_OPERATORS:
            return
        section = "LAYOUT_" + self.current_user

        ini = configparser.ConfigParser()
        ini.read( ["happyscript.ini"] )
        
        # restore window and pane position
        
        if ini.has_section(section):
            x = ini.getint(section, "WindowX")
            y = ini.getint(section, "WindowY")
            width = ini.getint(section, "WindowWidht" )
            height = ini.getint(section, "WindowHeight" )
            
            self.SetPosition((x,y))
            self.SetSize((width, height))
            
            if ini.has_option(section, "pane_layout"):
                panes = ini.get(section, "pane_layout")
                try:
                    self.m_mgr.LoadPerspective(panes, False)
                except:
                    pass


    def SavePosition( self, also_save_user = False ):
        ''' Save the position of the window and the panes
        '''
        if self.current_user not in self.VALID_OPERATORS:
            return
        
        section = "LAYOUT_" + self.current_user
        
        x, y = self.GetPosition()
        width, height = self.GetSize()
        
        ini = configparser.ConfigParser()
        ini.read( ["happyscript.ini"] )
        if not ini.has_section(section):
            ini.add_section(section)
        ini.set(section, "WindowX", str(x) )
        ini.set(section, "WindowY", str(y) )
        ini.set(section, "WindowWidht", str(width) )
        ini.set(section, "WindowHeight", str(height) )
        
        ini.set(section, "pane_layout", self.m_mgr.SavePerspective() )
        
        if also_save_user:
            if not ini.has_section("varia"):
                ini.add_section("varia")
            ini.set("varia", "CurrentUser", self.current_user )
                        
        with open("happyscript.ini", "w") as inifile:
            ini.write(inifile)

    def OnFormClose(self, event):
        self.m_guiTimer.Stop()
        FormOnTestFailure.cleanup()                     # destroy 'failure' form if necessary
        FormSerials.cleanup()
        self.SavePosition(True)
        self.m_mgr.UnInit()                                          # deinitialize the frame manager
        
        self.Destroy()                                              # delete the frame
        wx.GetApp().ExitMainLoop()

    def TogglePanel(self, panel):
        pane = self.m_mgr.GetPane(panel)
        if pane.IsShown():
            if pane.IsDocked():
                pane.Float()
            pane.Show(False)
        else:
            pane.Dock()
            pane.Show(True)
        self.m_mgr.Update()

    def OnBtnScripts( self, event ):
        self.TogglePanel(self._nbk_scripts)

    def OnBtnPython( self, event ):
        self.TogglePanel(self._shell_window)

    def OnBtnLogging( self, event ):
        self.TogglePanel(self.logPane)

    def OnBtnMessages( self, event ):
        self.TogglePanel(self.msgArea)

    def OnBtnTestList( self, event ):
        self.TogglePanel(self.pnlTests)

    def OnBtnCharts( self, event ):
        self.TogglePanel(self.chartsPane)

    def OnBtnControls( self, event ):
        self.TogglePanel(self._nbk_control_panels)

    def OnLayoutOperator( self, event ):
        self.SwitchUser("OPERATOR")
        
    def OnLayoutTechnician( self, event ):
        self.SwitchUser("TECHNICIAN")

    def OnLayoutEngineer( self, event ):
        self.SwitchUser("ENGINEER")

    def OnLayoutExpert( self, event ):
        self.SwitchUser("EXPERT")

    def OnResetLayout( self, event ):
        event.Skip()

    def OnBtnExit( self, event ):
        self.Close()

    def PushShellCommand(self, cmd):
        ''' Push a command in the Python shell window.
        '''
        self._shell_window.push(cmd, True)

    def OnGuiTimer( self, event ):
        if self.on_gui_timer is not None:
            self.on_gui_timer()
            
        if self.on_log_timer is not None:
            self.on_log_timer()

    def ClearLogs(self):
        ''' Clears the logs in the message area and the log window.
        '''
        self.msgArea.clear()
        self.logPane.clear()

    def OnMnuSettingsClicked( self, event ):
        self._script_manager.show_settings() 

    def DisableSettingsButton(self):
        ''' Disable the settings button in the toolbar.
            This is used when no ini file is set.
        '''
        self.m_mnuToolbar.EnableTool(self.m_btnSettings.GetId(), False)
        # self.m_btnSettings.Hide()
