# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class PanelScripts_Base
###########################################################################

class PanelScripts_Base ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,477 ), style = 0, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer54 = wx.BoxSizer( wx.VERTICAL )

		bSizer64 = wx.BoxSizer( wx.HORIZONTAL )

		self.btn_stop = wx.Button( self, wx.ID_ANY, u"Stop script", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btn_stop.SetToolTip( u"Stop script by setting a software flag.  Scripts must stop on their own in a controlled manner." )

		bSizer64.Add( self.btn_stop, 3, wx.ALL, 5 )


		bSizer64.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_btnReload = wx.Button( self, wx.ID_ANY, u"Reload", wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_EXACTFIT )
		bSizer64.Add( self.m_btnReload, 2, wx.ALL, 5 )


		bSizer54.Add( bSizer64, 0, wx.EXPAND, 5 )

		self.m_splitter2 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter2.SetSashGravity( 0.9 )
		self.m_splitter2.Bind( wx.EVT_IDLE, self.m_splitter2OnIdle )

		self.m_panel1 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer58 = wx.BoxSizer( wx.VERTICAL )

		self.treeScripts = wx.TreeCtrl( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		bSizer58.Add( self.treeScripts, 1, wx.ALL|wx.EXPAND, 5 )


		self.m_panel1.SetSizer( bSizer58 )
		self.m_panel1.Layout()
		bSizer58.Fit( self.m_panel1 )
		self.m_panel2 = wx.Panel( self.m_splitter2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel2.SetMaxSize( wx.Size( -1,200 ) )

		bSizer59 = wx.BoxSizer( wx.VERTICAL )

		self.txtHelp = wx.TextCtrl( self.m_panel2, wx.ID_ANY, u"This command initializes the coprocessor test setup. Also this will do a lot of other things that won't be described here.", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
		bSizer59.Add( self.txtHelp, 1, wx.ALL|wx.EXPAND, 5 )


		self.m_panel2.SetSizer( bSizer59 )
		self.m_panel2.Layout()
		bSizer59.Fit( self.m_panel2 )
		self.m_splitter2.SplitHorizontally( self.m_panel1, self.m_panel2, 0 )
		bSizer54.Add( self.m_splitter2, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer54 )
		self.Layout()

		# Connect Events
		self.btn_stop.Bind( wx.EVT_BUTTON, self.btn_stopOnButtonClick )
		self.m_btnReload.Bind( wx.EVT_BUTTON, self.OnBtnReload )
		self.treeScripts.Bind( wx.EVT_LEFT_DCLICK, self.OnTreeLeftDoubleClick )
		self.treeScripts.Bind( wx.EVT_TREE_KEY_DOWN, self.OnTreeKeyDown )
		self.treeScripts.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def btn_stopOnButtonClick( self, event ):
		event.Skip()

	def OnBtnReload( self, event ):
		event.Skip()

	def OnTreeLeftDoubleClick( self, event ):
		event.Skip()

	def OnTreeKeyDown( self, event ):
		event.Skip()

	def OnTreeSelChanged( self, event ):
		event.Skip()

	def m_splitter2OnIdle( self, event ):
		self.m_splitter2.SetSashPosition( 0 )
		self.m_splitter2.Unbind( wx.EVT_IDLE )


###########################################################################
## Class PanelMessages_Base
###########################################################################

class PanelMessages_Base ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,562 ), style = 0, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnClearList = wx.Button( self, wx.ID_ANY, u"Clear list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.btnClearList, 0, wx.ALL, 5 )


		bSizer6.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"Log Level", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		bSizer6.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		m_cboLogLevelChoices = [ u"Debug", u"Info", u"Warning" ]
		self.m_cboLogLevel = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_cboLogLevelChoices, 0 )
		self.m_cboLogLevel.SetSelection( 2 )
		bSizer6.Add( self.m_cboLogLevel, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer6, 0, wx.EXPAND, 5 )

		self.lstMessages = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		bSizer5.Add( self.lstMessages, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer5 )
		self.Layout()

		# Connect Events
		self.btnClearList.Bind( wx.EVT_BUTTON, self.OnBtnClearList )
		self.m_cboLogLevel.Bind( wx.EVT_CHOICE, self.OnSelectLogLevel )
		self.lstMessages.Bind( wx.EVT_SIZE, self.OnListSize )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnBtnClearList( self, event ):
		event.Skip()

	def OnSelectLogLevel( self, event ):
		event.Skip()

	def OnListSize( self, event ):
		event.Skip()


###########################################################################
## Class PanelLog_Base
###########################################################################

class PanelLog_Base ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 783,466 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer7 = wx.BoxSizer( wx.VERTICAL )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_btnClearLog = wx.Button( self, wx.ID_ANY, u"Clear Log", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_btnClearLog, 0, wx.ALL, 5 )


		bSizer17.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_btnStop = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnStop.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.m_btnStop.SetToolTip( u"Stop logging.  Handy if you want to copy-paste something." )

		bSizer17.Add( self.m_btnStop, 0, wx.ALL, 5 )

		self.m_btnResume = wx.Button( self, wx.ID_ANY, u"Resume", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnResume.Enable( False )
		self.m_btnResume.SetToolTip( u"Resume logging, after being stopped." )

		bSizer17.Add( self.m_btnResume, 0, wx.ALL, 5 )


		bSizer17.Add( ( 0, 0), 6, wx.EXPAND, 5 )

		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Log  level", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )

		bSizer17.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		m_cboLogLevelChoices = [ u"Debug", u"Info", u"Warning" ]
		self.m_cboLogLevel = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_cboLogLevelChoices, 0 )
		self.m_cboLogLevel.SetSelection( 1 )
		bSizer17.Add( self.m_cboLogLevel, 0, wx.ALL, 5 )


		bSizer7.Add( bSizer17, 1, wx.EXPAND, 5 )

		self.wx_txtLog = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		self.wx_txtLog.SetFont( wx.Font( 10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas" ) )

		bSizer7.Add( self.wx_txtLog, 100, wx.ALL|wx.EXPAND, 5 )

		self.wx_txtCommand = wx.TextCtrl( self, wx.ID_ANY, u"Type command here", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.wx_txtCommand.SetFont( wx.Font( 10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas" ) )

		bSizer7.Add( self.wx_txtCommand, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer7 )
		self.Layout()

		# Connect Events
		self.m_btnClearLog.Bind( wx.EVT_BUTTON, self.OnBtnClearLog )
		self.m_btnStop.Bind( wx.EVT_BUTTON, self.OnBtnStop )
		self.m_btnResume.Bind( wx.EVT_BUTTON, self.OnBtnResume )
		self.m_cboLogLevel.Bind( wx.EVT_CHOICE, self.OnSelectLogLevel )
		self.wx_txtCommand.Bind( wx.EVT_KEY_UP, self.OnCmdKeyUp )
		self.wx_txtCommand.Bind( wx.EVT_SET_FOCUS, self.OnSetFocus )
		self.wx_txtCommand.Bind( wx.EVT_TEXT_ENTER, self.OnCmdEnter )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnBtnClearLog( self, event ):
		event.Skip()

	def OnBtnStop( self, event ):
		event.Skip()

	def OnBtnResume( self, event ):
		event.Skip()

	def OnSelectLogLevel( self, event ):
		event.Skip()

	def OnCmdKeyUp( self, event ):
		event.Skip()

	def OnSetFocus( self, event ):
		event.Skip()

	def OnCmdEnter( self, event ):
		event.Skip()


###########################################################################
## Class PanelTests_Base
###########################################################################

class PanelTests_Base ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = 0, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer8 = wx.BoxSizer( wx.VERTICAL )

		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_btnStart = wx.Button( self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnStart.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer9.Add( self.m_btnStart, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_btnPause = wx.Button( self, wx.ID_ANY, u"Pause", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnPause.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_btnPause.Enable( False )

		bSizer9.Add( self.m_btnPause, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_btnStop = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnStop.SetFont( wx.Font( 14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_btnStop.Enable( False )

		bSizer9.Add( self.m_btnStop, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer8.Add( bSizer9, 0, wx.EXPAND, 5 )

		self.m_txtStatus = wx.StaticText( self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtStatus.Wrap( -1 )

		self.m_txtStatus.SetFont( wx.Font( 16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer8.Add( self.m_txtStatus, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		self.m_lstTests = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT )
		self.m_lstTests.SetFont( wx.Font( 12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_lstTests.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		bSizer8.Add( self.m_lstTests, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer8 )
		self.Layout()
		self.m_tmrStateMachine = wx.Timer()
		self.m_tmrStateMachine.SetOwner( self, wx.ID_ANY )
		self.m_mnuTestList = wx.Menu()
		self.m_mniRun = wx.MenuItem( self.m_mnuTestList, wx.ID_ANY, u"Run now", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniRun.SetBitmap( wx.ArtProvider.GetBitmap( "play",  ) )
		self.m_mnuTestList.Append( self.m_mniRun )

		self.m_mnuTestList.AppendSeparator()

		self.m_mniEnable = wx.MenuItem( self.m_mnuTestList, wx.ID_ANY, u"Enable", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniEnable.SetBitmap( wx.ArtProvider.GetBitmap( "idle",  ) )
		self.m_mnuTestList.Append( self.m_mniEnable )

		self.m_mniDisable = wx.MenuItem( self.m_mnuTestList, wx.ID_ANY, u"Disable", u"Test will not run, and it will count as a failed test.", wx.ITEM_NORMAL )
		self.m_mniDisable.SetBitmap( wx.ArtProvider.GetBitmap( "disable",  ) )
		self.m_mnuTestList.Append( self.m_mniDisable )

		self.m_mniSkip = wx.MenuItem( self.m_mnuTestList, wx.ID_ANY, u"Skip", u"Test is not run, and is considered successful", wx.ITEM_NORMAL )
		self.m_mniSkip.SetBitmap( wx.ArtProvider.GetBitmap( "skip",  ) )
		self.m_mnuTestList.Append( self.m_mniSkip )

		self.m_mnuTestList.AppendSeparator()

		self.m_mniBreakpoint = wx.MenuItem( self.m_mnuTestList, wx.ID_ANY, u"Toggle breakpoint", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniBreakpoint.SetBitmap( wx.ArtProvider.GetBitmap( "red_dot",  ) )
		self.m_mnuTestList.Append( self.m_mniBreakpoint )



		# Connect Events
		self.m_btnStart.Bind( wx.EVT_BUTTON, self.OnBtnStartClick )
		self.m_btnPause.Bind( wx.EVT_BUTTON, self.OnBtnPauseClick )
		self.m_btnStop.Bind( wx.EVT_BUTTON, self.OnBtnStopClick )
		self.m_lstTests.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnListRightClick )
		self.m_lstTests.Bind( wx.EVT_SIZE, self.OnListSize )
		self.Bind( wx.EVT_TIMER, self.OnTmrStateMachine, id=wx.ID_ANY )
		self.Bind( wx.EVT_MENU, self.OnMenuRun, id = self.m_mniRun.GetId() )
		self.Bind( wx.EVT_MENU, self.OnMenuEnable, id = self.m_mniEnable.GetId() )
		self.Bind( wx.EVT_MENU, self.OnMenudisable, id = self.m_mniDisable.GetId() )
		self.Bind( wx.EVT_MENU, self.OnMenuSkip, id = self.m_mniSkip.GetId() )
		self.Bind( wx.EVT_MENU, self.OnMenuBreakpoint, id = self.m_mniBreakpoint.GetId() )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnBtnStartClick( self, event ):
		event.Skip()

	def OnBtnPauseClick( self, event ):
		event.Skip()

	def OnBtnStopClick( self, event ):
		event.Skip()

	def OnListRightClick( self, event ):
		event.Skip()

	def OnListSize( self, event ):
		event.Skip()

	def OnTmrStateMachine( self, event ):
		event.Skip()

	def OnMenuRun( self, event ):
		event.Skip()

	def OnMenuEnable( self, event ):
		event.Skip()

	def OnMenudisable( self, event ):
		event.Skip()

	def OnMenuSkip( self, event ):
		event.Skip()

	def OnMenuBreakpoint( self, event ):
		event.Skip()


###########################################################################
## Class PanelCharts_Base
###########################################################################

class PanelCharts_Base ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		m_sizerTop = wx.BoxSizer( wx.HORIZONTAL )

		self.m_nbkPlots = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		m_sizerTop.Add( self.m_nbkPlots, 1, wx.EXPAND |wx.ALL, 5 )

		bSizer19 = wx.BoxSizer( wx.VERTICAL )

		self.m_btnCopyData = wx.Button( self, wx.ID_ANY, u"Copy data", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_btnCopyData, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer19.Add( ( 0, 10), 0, wx.EXPAND, 5 )

		self.m_btnAntiAlias = wx.Button( self, wx.ID_ANY, u"Make pretty", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_btnAntiAlias, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_btnSaveToFile = wx.Button( self, wx.ID_ANY, u"Save bitmap...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_btnSaveToFile, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer19.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		m_rbxMouseModeChoices = [ u"Fixed", u"Zoom", u"Move" ]
		self.m_rbxMouseMode = wx.RadioBox( self, wx.ID_ANY, u"Mouse mode", wx.DefaultPosition, wx.DefaultSize, m_rbxMouseModeChoices, 1, wx.RA_SPECIFY_COLS )
		self.m_rbxMouseMode.SetSelection( 0 )
		bSizer19.Add( self.m_rbxMouseMode, 0, wx.ALL, 5 )


		m_sizerTop.Add( bSizer19, 0, wx.EXPAND, 5 )


		self.SetSizer( m_sizerTop )
		self.Layout()
		self.m_tmrAnimate = wx.Timer()
		self.m_tmrAnimate.SetOwner( self, wx.ID_ANY )
		self.m_tmrRedraw = wx.Timer()
		self.m_tmrRedraw.SetOwner( self, wx.ID_ANY )
		self.m_tmrRedraw.Start( 50 )


		# Connect Events
		self.m_btnCopyData.Bind( wx.EVT_BUTTON, self.BtnCopyDataClick )
		self.m_btnAntiAlias.Bind( wx.EVT_BUTTON, self.OnMakePretty )
		self.m_btnSaveToFile.Bind( wx.EVT_BUTTON, self.OnBtnSaveBitmap )
		self.m_rbxMouseMode.Bind( wx.EVT_RADIOBOX, self.OnRadioBoxMouseMode )
		self.Bind( wx.EVT_TIMER, self.OnTimerAnimate, id=wx.ID_ANY )
		self.Bind( wx.EVT_TIMER, self.OnRedrawTimer, id=wx.ID_ANY )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def BtnCopyDataClick( self, event ):
		event.Skip()

	def OnMakePretty( self, event ):
		event.Skip()

	def OnBtnSaveBitmap( self, event ):
		event.Skip()

	def OnRadioBoxMouseMode( self, event ):
		event.Skip()

	def OnTimerAnimate( self, event ):
		event.Skip()

	def OnRedrawTimer( self, event ):
		event.Skip()


###########################################################################
## Class PlotDialog
###########################################################################

class PlotDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer21 = wx.BoxSizer( wx.VERTICAL )

		self.m_thePanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer21.Add( self.m_thePanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer21 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnClose( self, event ):
		event.Skip()


