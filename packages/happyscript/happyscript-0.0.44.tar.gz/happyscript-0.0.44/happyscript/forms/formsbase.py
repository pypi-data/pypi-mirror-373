# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui

ID_BTN_TESTLIST = 6000
ID_BTN_MESSAGES = 6001
ID_BTN_LOGGING = 6002
ID_BTN_SCRIPTS = 6003
ID_BTN_PYTHON = 6004
ID_BTN_CONTROLS = 6005
ID_BTN_CHARTS = 6006

###########################################################################
## Class FormMain_Base
###########################################################################

class FormMain_Base ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"HappyScript -", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.m_mgr = wx.aui.AuiManager()
		self.m_mgr.SetManagedWindow( self )
		self.m_mgr.SetFlags(wx.aui.AUI_MGR_ALLOW_FLOATING|wx.aui.AUI_MGR_RECTANGLE_HINT|wx.aui.AUI_MGR_TRANSPARENT_HINT)

		self.m_guiTimer = wx.Timer()
		self.m_guiTimer.SetOwner( self, self.m_guiTimer.GetId() )
		self.m_mnuToolbar = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_TEXT )
		self.m_mnuToolbar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_mnuToolbar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		self.m_btnLayout = self.m_mnuToolbar.AddTool( wx.ID_ANY, u"User", wx.ArtProvider.GetBitmap( "layout_DD",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnSettings = self.m_mnuToolbar.AddTool( wx.ID_ANY, u"Settings", wx.ArtProvider.GetBitmap( "settings",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_mnuToolbar.AddSeparator()

		self.m_btnTestList = self.m_mnuToolbar.AddTool( ID_BTN_TESTLIST, u"Tests", wx.ArtProvider.GetBitmap( "tests",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnMessages = self.m_mnuToolbar.AddTool( ID_BTN_MESSAGES, u"Messages", wx.ArtProvider.GetBitmap( "messages",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnLogging = self.m_mnuToolbar.AddTool( ID_BTN_LOGGING, u"Logging", wx.ArtProvider.GetBitmap( "logging",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnScripts = self.m_mnuToolbar.AddTool( ID_BTN_SCRIPTS, u"Scripts", wx.ArtProvider.GetBitmap( "script_list",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnPython = self.m_mnuToolbar.AddTool( ID_BTN_PYTHON, u"Python", wx.ArtProvider.GetBitmap( "python",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnControls = self.m_mnuToolbar.AddTool( ID_BTN_CONTROLS, u"Controls", wx.ArtProvider.GetBitmap( "control_panel",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_btnCharts = self.m_mnuToolbar.AddTool( ID_BTN_CHARTS, u"Charts", wx.ArtProvider.GetBitmap( "charts",  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_mnuToolbar.AddSeparator()

		self.m_btnExit = self.m_mnuToolbar.AddTool( wx.ID_ANY, u"Exit", wx.ArtProvider.GetBitmap( wx.ART_QUIT,  ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_mnuToolbar.Realize()
		self.m_mgr.AddPane( self.m_mnuToolbar, wx.aui.AuiPaneInfo() .Name( u"dfasdf" ).Top() .Caption( u"ZXcZXcZXcZXC" ).CaptionVisible( False ).CloseButton( False ).PaneBorder( False ).Movable( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).BottomDockable( False ).TopDockable( False ).LeftDockable( False ).RightDockable( False ).Floatable( False ).Layer( 3 ) )

		self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_mnuLayout = wx.Menu()
		self.m_mniLayoutOperator = wx.MenuItem( self.m_mnuLayout, wx.ID_ANY, u"Operator", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniLayoutOperator.SetBitmap( wx.ArtProvider.GetBitmap( "user_operator",  ) )
		self.m_mnuLayout.Append( self.m_mniLayoutOperator )

		self.m_mniLayoutTechnician = wx.MenuItem( self.m_mnuLayout, wx.ID_ANY, u"Technician", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniLayoutTechnician.SetBitmap( wx.ArtProvider.GetBitmap( "user_technician",  ) )
		self.m_mnuLayout.Append( self.m_mniLayoutTechnician )

		self.m_mniLayoutEngineer = wx.MenuItem( self.m_mnuLayout, wx.ID_ANY, u"Engineer", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniLayoutEngineer.SetBitmap( wx.ArtProvider.GetBitmap( "user_engineer",  ) )
		self.m_mnuLayout.Append( self.m_mniLayoutEngineer )

		self.m_mniLayoutExpert = wx.MenuItem( self.m_mnuLayout, wx.ID_ANY, u"Expert", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniLayoutExpert.SetBitmap( wx.ArtProvider.GetBitmap( "user_expert",  ) )
		self.m_mnuLayout.Append( self.m_mniLayoutExpert )

		self.m_mnuLayout.AppendSeparator()

		self.m_mniLayoutReset = wx.MenuItem( self.m_mnuLayout, wx.ID_ANY, u"Reset to default", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mniLayoutReset.SetBitmap( wx.ArtProvider.GetBitmap( "reset",  ) )
		self.m_mnuLayout.Append( self.m_mniLayoutReset )
		self.m_mniLayoutReset.Enable( False )



		self.m_mgr.Update()
		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnFormClose )
		self.Bind( wx.EVT_TIMER, self.OnGuiTimer, id=self.m_guiTimer.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnMnuLayoutClicked, id = self.m_btnLayout.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnMnuSettingsClicked, id = self.m_btnSettings.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnTestList, id = self.m_btnTestList.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnMessages, id = self.m_btnMessages.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnLogging, id = self.m_btnLogging.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnScripts, id = self.m_btnScripts.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnPython, id = self.m_btnPython.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnControls, id = self.m_btnControls.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnCharts, id = self.m_btnCharts.GetId() )
		self.Bind( wx.EVT_TOOL, self.OnBtnExit, id = self.m_btnExit.GetId() )
		self.Bind( wx.EVT_MENU, self.OnLayoutOperator, id = self.m_mniLayoutOperator.GetId() )
		self.Bind( wx.EVT_MENU, self.OnLayoutTechnician, id = self.m_mniLayoutTechnician.GetId() )
		self.Bind( wx.EVT_MENU, self.OnLayoutEngineer, id = self.m_mniLayoutEngineer.GetId() )
		self.Bind( wx.EVT_MENU, self.OnLayoutExpert, id = self.m_mniLayoutExpert.GetId() )
		self.Bind( wx.EVT_MENU, self.OnResetLayout, id = self.m_mniLayoutReset.GetId() )

	def __del__( self ):
		self.m_mgr.UnInit()



	# Virtual event handlers, override them in your derived class
	def OnFormClose( self, event ):
		event.Skip()

	def OnGuiTimer( self, event ):
		event.Skip()

	def OnMnuLayoutClicked( self, event ):
		event.Skip()

	def OnMnuSettingsClicked( self, event ):
		event.Skip()

	def OnBtnTestList( self, event ):
		event.Skip()

	def OnBtnMessages( self, event ):
		event.Skip()

	def OnBtnLogging( self, event ):
		event.Skip()

	def OnBtnScripts( self, event ):
		event.Skip()

	def OnBtnPython( self, event ):
		event.Skip()

	def OnBtnControls( self, event ):
		event.Skip()

	def OnBtnCharts( self, event ):
		event.Skip()

	def OnBtnExit( self, event ):
		event.Skip()

	def OnLayoutOperator( self, event ):
		event.Skip()

	def OnLayoutTechnician( self, event ):
		event.Skip()

	def OnLayoutEngineer( self, event ):
		event.Skip()

	def OnLayoutExpert( self, event ):
		event.Skip()

	def OnResetLayout( self, event ):
		event.Skip()


###########################################################################
## Class FormSerials_Base
###########################################################################

class FormSerials_Base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Scan serial numbers", pos = wx.DefaultPosition, size = wx.Size( 400,431 ), style = 0 )

		self.SetSizeHints( wx.DefaultSize, wx.Size( 400,500 ) )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Scan serial numbers :", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		bSizer10.Add( self.m_staticText8, 0, wx.ALL, 5 )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_lblSerial1 = wx.StaticText( self, wx.ID_ANY, u"Board 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial1.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial1, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial1.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial1, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial2 = wx.StaticText( self, wx.ID_ANY, u"Board 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial2.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial2, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial2.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial2, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial3 = wx.StaticText( self, wx.ID_ANY, u"Board 3", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial3.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial3, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial3.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial3, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial4 = wx.StaticText( self, wx.ID_ANY, u"Board 4", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial4.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial4, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial4 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial4.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial4, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial5 = wx.StaticText( self, wx.ID_ANY, u"Board 5", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial5.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial5, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial5 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial5.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial5, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial6 = wx.StaticText( self, wx.ID_ANY, u"Board 6", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial6.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial6, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial6.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial6, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial7 = wx.StaticText( self, wx.ID_ANY, u"Board 7", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial7.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial7, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial7 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial7.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial7, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial8 = wx.StaticText( self, wx.ID_ANY, u"Board 8", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial8.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial8, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial8 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial8.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial8, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial9 = wx.StaticText( self, wx.ID_ANY, u"Board 9", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial9.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial9, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial9 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial9.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial9, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_lblSerial10 = wx.StaticText( self, wx.ID_ANY, u"Board 10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblSerial10.Wrap( -1 )

		gSizer1.Add( self.m_lblSerial10, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_txtSerial10 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.m_txtSerial10.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		gSizer1.Add( self.m_txtSerial10, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer10.Add( gSizer1, 1, wx.EXPAND, 5 )


		bSizer10.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_btnOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
		bSizer12.Add( self.m_btnOK, 3, wx.ALL, 5 )


		bSizer12.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.Size( -1,40 ), 0 )
		bSizer12.Add( self.m_btnCancel, 2, wx.ALL, 5 )


		bSizer10.Add( bSizer12, 2, wx.EXPAND, 10 )


		self.SetSizer( bSizer10 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_txtSerial1.Bind( wx.EVT_TEXT, self.OnText1 )
		self.m_txtSerial1.Bind( wx.EVT_TEXT_ENTER, self.OnEnter1 )
		self.m_txtSerial2.Bind( wx.EVT_TEXT, self.OnText2 )
		self.m_txtSerial2.Bind( wx.EVT_TEXT_ENTER, self.OnEnter2 )
		self.m_txtSerial3.Bind( wx.EVT_TEXT, self.OnText3 )
		self.m_txtSerial3.Bind( wx.EVT_TEXT_ENTER, self.OnEnter3 )
		self.m_txtSerial4.Bind( wx.EVT_TEXT, self.OnText4 )
		self.m_txtSerial4.Bind( wx.EVT_TEXT_ENTER, self.OnEnter4 )
		self.m_txtSerial5.Bind( wx.EVT_TEXT, self.OnText5 )
		self.m_txtSerial5.Bind( wx.EVT_TEXT_ENTER, self.OnEnter5 )
		self.m_txtSerial6.Bind( wx.EVT_TEXT, self.OnText6 )
		self.m_txtSerial6.Bind( wx.EVT_TEXT_ENTER, self.OnEnter6 )
		self.m_txtSerial7.Bind( wx.EVT_TEXT, self.OnText7 )
		self.m_txtSerial7.Bind( wx.EVT_TEXT_ENTER, self.OnEnter7 )
		self.m_txtSerial8.Bind( wx.EVT_TEXT, self.OnText8 )
		self.m_txtSerial8.Bind( wx.EVT_TEXT_ENTER, self.OnEnter8 )
		self.m_txtSerial9.Bind( wx.EVT_TEXT, self.OnText9 )
		self.m_txtSerial9.Bind( wx.EVT_TEXT_ENTER, self.OnEnter9 )
		self.m_txtSerial10.Bind( wx.EVT_TEXT, self.OnText10 )
		self.m_txtSerial10.Bind( wx.EVT_TEXT_ENTER, self.OnEnter10 )
		self.m_btnOK.Bind( wx.EVT_BUTTON, self.OnBtnOK )
		self.m_btnCancel.Bind( wx.EVT_BUTTON, self.OnBtnCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnText1( self, event ):
		event.Skip()

	def OnEnter1( self, event ):
		event.Skip()

	def OnText2( self, event ):
		event.Skip()

	def OnEnter2( self, event ):
		event.Skip()

	def OnText3( self, event ):
		event.Skip()

	def OnEnter3( self, event ):
		event.Skip()

	def OnText4( self, event ):
		event.Skip()

	def OnEnter4( self, event ):
		event.Skip()

	def OnText5( self, event ):
		event.Skip()

	def OnEnter5( self, event ):
		event.Skip()

	def OnText6( self, event ):
		event.Skip()

	def OnEnter6( self, event ):
		event.Skip()

	def OnText7( self, event ):
		event.Skip()

	def OnEnter7( self, event ):
		event.Skip()

	def OnText8( self, event ):
		event.Skip()

	def OnEnter8( self, event ):
		event.Skip()

	def OnText9( self, event ):
		event.Skip()

	def OnEnter9( self, event ):
		event.Skip()

	def OnText10( self, event ):
		event.Skip()

	def OnEnter10( self, event ):
		event.Skip()

	def OnBtnOK( self, event ):
		event.Skip()

	def OnBtnCancel( self, event ):
		event.Skip()


###########################################################################
## Class FormAskImage_Base
###########################################################################

class FormAskImage_Base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"HappyScript", pos = wx.DefaultPosition, size = wx.Size( 318,338 ), style = wx.CAPTION|wx.STAY_ON_TOP )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer12.Add( self.m_bitmap, 9, wx.ALL|wx.EXPAND, 5 )

		m_sizeButtons = wx.BoxSizer( wx.VERTICAL )


		m_sizeButtons.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_txtMessage = wx.StaticText( self, wx.ID_ANY, u"Message provided by script\nCould be several lines long.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtMessage.Wrap( -1 )

		m_sizeButtons.Add( self.m_txtMessage, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_txtValue = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		m_sizeButtons.Add( self.m_txtValue, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_btnOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_btnOK.SetDefault()
		self.m_btnOK.SetMinSize( wx.Size( -1,40 ) )

		m_sizeButtons.Add( self.m_btnOK, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_btnNo = wx.Button( self, wx.ID_ANY, u"No", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnNo.SetMinSize( wx.Size( -1,40 ) )

		m_sizeButtons.Add( self.m_btnNo, 0, wx.ALL|wx.EXPAND, 5 )


		m_sizeButtons.Add( ( 0, 0), 10, wx.EXPAND, 5 )

		self.m_btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnCancel.SetMinSize( wx.Size( -1,40 ) )

		m_sizeButtons.Add( self.m_btnCancel, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer12.Add( m_sizeButtons, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer12 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_btnOK.Bind( wx.EVT_BUTTON, self.OnButtonOK )
		self.m_btnNo.Bind( wx.EVT_BUTTON, self.OnButtonNo )
		self.m_btnCancel.Bind( wx.EVT_BUTTON, self.OnButtonCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnButtonOK( self, event ):
		event.Skip()

	def OnButtonNo( self, event ):
		event.Skip()

	def OnButtonCancel( self, event ):
		event.Skip()


###########################################################################
## Class FormAskChoice_Base
###########################################################################

class FormAskChoice_Base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"HappyScript", pos = wx.DefaultPosition, size = wx.Size( 318,227 ), style = wx.CAPTION|wx.STAY_ON_TOP )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer12 = wx.BoxSizer( wx.VERTICAL )

		self.m_txtMessage = wx.StaticText( self, wx.ID_ANY, u"Message provided by script\nCould be several lines long.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtMessage.Wrap( -1 )

		self.m_txtMessage.SetFont( wx.Font( 11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )

		bSizer12.Add( self.m_txtMessage, 0, wx.ALL|wx.EXPAND, 10 )

		self.m_pnlChoices = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_THEME|wx.TAB_TRAVERSAL )
		bSizer12.Add( self.m_pnlChoices, 1, wx.EXPAND |wx.ALL, 15 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_btnOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_btnOK.SetDefault()
		self.m_btnOK.SetFont( wx.Font( 11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_btnOK.Enable( False )
		self.m_btnOK.SetMinSize( wx.Size( -1,40 ) )

		bSizer21.Add( self.m_btnOK, 5, wx.ALL|wx.EXPAND, 10 )


		bSizer21.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnCancel.SetFont( wx.Font( 11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_btnCancel.SetMinSize( wx.Size( -1,40 ) )

		bSizer21.Add( self.m_btnCancel, 2, wx.ALL|wx.EXPAND, 10 )


		bSizer12.Add( bSizer21, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer12 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_btnOK.Bind( wx.EVT_BUTTON, self.OnButtonOK )
		self.m_btnCancel.Bind( wx.EVT_BUTTON, self.OnButtonCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnButtonOK( self, event ):
		event.Skip()

	def OnButtonCancel( self, event ):
		event.Skip()


###########################################################################
## Class FormOnTestFailure_Base
###########################################################################

class FormOnTestFailure_Base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Error", pos = wx.DefaultPosition, size = wx.Size( 356,229 ), style = wx.CAPTION )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.SetBackgroundColour( wx.Colour( 255, 206, 206 ) )

		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.m_txtMessage = wx.StaticText( self, wx.ID_ANY, u"Test xxxx failed.\nWhat do you want to do ?", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_txtMessage.Wrap( -1 )

		self.m_txtMessage.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.m_txtMessage.SetForegroundColour( wx.Colour( 0, 0, 0 ) )

		bSizer14.Add( self.m_txtMessage, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_btnRetry = wx.Button( self, wx.ID_ANY, u"Repeat this test", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnRetry.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer14.Add( self.m_btnRetry, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_btnSkipTest = wx.Button( self, wx.ID_ANY, u"Skip this test", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnSkipTest.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer14.Add( self.m_btnSkipTest, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_btnStopTests = wx.Button( self, wx.ID_ANY, u"Stop all tests", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnStopTests.SetFont( wx.Font( 12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer14.Add( self.m_btnStopTests, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer14 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_btnRetry.Bind( wx.EVT_BUTTON, self.OnBtnRetry )
		self.m_btnSkipTest.Bind( wx.EVT_BUTTON, self.OnBtnSkip )
		self.m_btnStopTests.Bind( wx.EVT_BUTTON, self.OnBtnStop )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnBtnRetry( self, event ):
		event.Skip()

	def OnBtnSkip( self, event ):
		event.Skip()

	def OnBtnStop( self, event ):
		event.Skip()


###########################################################################
## Class FormStop_base
###########################################################################

class FormStop_base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Happyscript", pos = wx.DefaultPosition, size = wx.Size( 480,198 ), style = wx.CAPTION|wx.STAY_ON_TOP )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.m_lblMessage = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_lblMessage.Wrap( -1 )

		bSizer14.Add( self.m_lblMessage, 1, wx.ALL, 20 )

		self.m_btnCancel = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.m_btnCancel, 0, wx.ALL|wx.EXPAND, 20 )


		self.SetSizer( bSizer14 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_btnCancel.Bind( wx.EVT_BUTTON, self.OnBtnStop )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnBtnStop( self, event ):
		event.Skip()


###########################################################################
## Class FormSettings_Base
###########################################################################

class FormSettings_Base ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Settings", pos = wx.DefaultPosition, size = wx.Size( 543,623 ), style = wx.CAPTION|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 320,240 ), wx.DefaultSize )

		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		self.Scroll = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL )
		self.Scroll.SetScrollRate( 5, 5 )
		ScrollSizer = wx.BoxSizer( wx.VERTICAL )

		delete_me = wx.StaticBoxSizer( wx.StaticBox( self.Scroll, wx.ID_ANY, u"toy" ), wx.VERTICAL )

		fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer1.AddGrowableCol( 1 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText21 = wx.StaticText( delete_me.GetStaticBox(), wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )

		fgSizer1.Add( self.m_staticText21, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

		self.m_textCtrl17 = wx.TextCtrl( delete_me.GetStaticBox(), wx.ID_ANY, u"Dit is een test", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer1.Add( self.m_textCtrl17, 5, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText22 = wx.StaticText( delete_me.GetStaticBox(), wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText22.Wrap( -1 )

		fgSizer1.Add( self.m_staticText22, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

		self.m_textCtrl18 = wx.TextCtrl( delete_me.GetStaticBox(), wx.ID_ANY, u"Nog een test", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer1.Add( self.m_textCtrl18, 5, wx.ALL|wx.EXPAND, 5 )


		delete_me.Add( fgSizer1, 1, wx.EXPAND, 5 )


		ScrollSizer.Add( delete_me, 0, wx.EXPAND, 5 )


		ScrollSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.Scroll.SetSizer( ScrollSizer )
		self.Scroll.Layout()
		ScrollSizer.Fit( self.Scroll )
		bSizer9.Add( self.Scroll, 1, wx.EXPAND |wx.ALL, 5 )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		self.btnApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnApply.SetMinSize( wx.Size( -1,40 ) )

		bSizer10.Add( self.btnApply, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnCancel.SetMinSize( wx.Size( -1,40 ) )

		bSizer10.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer10.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer9.Add( bSizer10, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnApply.Bind( wx.EVT_BUTTON, self.OnBtnApply )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.OnBtnCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnBtnApply( self, event ):
		event.Skip()

	def OnBtnCancel( self, event ):
		event.Skip()


