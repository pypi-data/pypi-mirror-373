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
## Class SplashMenuMain_Base
###########################################################################

class SplashMenuMain_Base ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Menu", pos = wx.DefaultPosition, size = wx.Size( 629,523 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_SHAPED|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.STAY_ON_TOP|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		gSizer2 = wx.GridSizer( 2, 3, 0, 0 )

		self.m_bpButton2 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		gSizer2.Add( self.m_bpButton2, 0, wx.ALL, 5 )

		self.m_bpButton3 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		gSizer2.Add( self.m_bpButton3, 0, wx.ALL, 5 )

		self.m_bpButton4 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		gSizer2.Add( self.m_bpButton4, 0, wx.ALL, 5 )


		gSizer2.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_button24 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.m_button24, 0, wx.ALL, 5 )

		self.m_bpButton1 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )

		self.m_bpButton1.SetBitmap( wx.Bitmap( u"exit.png", wx.BITMAP_TYPE_ANY ) )
		gSizer2.Add( self.m_bpButton1, 0, wx.ALL|wx.EXPAND, 20 )


		bSizer16.Add( gSizer2, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()
		self.m_statusBar2 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_bpButton1.Bind( wx.EVT_BUTTON, self.DoExit )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def DoExit( self, event ):
		event.Skip()


