#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import wx
from .panelsbase import PanelScripts_Base

class PanelScripts2( PanelScripts_Base):
    ''' Panel containing a treeview of all scripts in a given directory.
    '''

    def __init__( self, parent, script_reader, script_control ):
        ''' @param parent         Control to put this panel in.  Typically a notebook.
            @param script_reader  ScriptReader object that read all the scripts in the script dir.
            @param script_control  Object run scripts
        '''
        PanelScripts_Base.__init__(self, parent)
    
        self._reader = script_reader
        self._script_ctrl = script_control
        
        self.tree_root = self.treeScripts.AddRoot("DUMMY")
        self.load_treeview()

    def load_treeview(self):
        ''' Load script names into the treeview.
        '''
        tree = self.treeScripts                                         # shorthand

        # make a list of all items that are expanded in the treeview
        expanded_files = list()
        (child, cookie) = tree.GetFirstChild(self.tree_root)
        while child.IsOk():
            if tree.IsExpanded(child):
                expanded_files.append(tree.GetItemText(child))
            (child, cookie) = tree.GetNextChild(self.tree_root, cookie)

        tree.DeleteChildren(self.tree_root)
        
        for modname in self._reader.get_file_list():
            child = tree.AppendItem(self.tree_root, modname)            # add item in treeview for file

            for funcname in self._reader.get_func_names(modname):
                tree.AppendItem(child, funcname)                        # add a child node to treeview

            if modname in expanded_files:                               # expand item if it was previously expanded
                tree.Expand(child)

    def OnBtnReload( self, event ):
        ''' Reloads all scripts of this directory.
        ''' 
        if self._script_ctrl.is_busy():
            msg = "A script is still running.  Press 'abort' first."
            wx.MessageBox( msg, "HappyScript", wx.OK | wx.ICON_WARNING )
            return
        
        self._reader.reload()
        self.load_treeview()

    def OnTreeLeftDoubleClick( self, event ):
        ''' Double-click on an item in the treeview.
            If it is a treeview node of the function it is executed.
            (Treeview nodes of a file have the root as parent, all others are functions.)
        '''
        pt = event.GetPosition();
        item, _ = self.treeScripts.HitTest(pt)
        self.ExecuteScriptForItem(item)


    def OnTreeKeyDown( self, event ):
        ''' Enter is pressed on an item in the treeview.
        '''
        keycode = event.GetKeyCode()
        if keycode==wx.WXK_RETURN:
            item = self.treeScripts.GetSelection()
            self.ExecuteScriptForItem(item)

    def ExecuteScriptForItem(self, item):
        ''' Execute a script of a treeview item.
            This is called either upon double-clicking on an item, or pressing ENTER.
        '''
        if item:
            parent = self.treeScripts.GetItemParent(item)
            if parent.IsOk() and parent!=self.tree_root:
                
                if self._script_ctrl.is_busy():
                    print("Another script is already running")
                else:
                    filename = self.treeScripts.GetItemText(parent)
                    funcname = self.treeScripts.GetItemText(item)
                    scriptname = "%s.%s.%s" % (self._reader.group_name, filename, funcname)
                    self._script_ctrl.run(scriptname)
         
    def OnTreeSelChanged( self, event ):
        ''' Update the description of the function when the selection in the treeview changes.
        '''
        txt = "no help"
        try:
            item = event.GetItem()
            if item:
                parent = self.treeScripts.GetItemParent(item)
                if parent.IsOk() and parent!=self.tree_root:
                    filename = self.treeScripts.GetItemText(parent)
                    funcname = self.treeScripts.GetItemText(item)
                    txt = self._reader.get_help(filename, funcname)
        except:
            pass
 
        self.txtHelp.SetValue(txt)
        event.Skip()

    def btn_stopOnButtonClick( self, event ):
        ''' Use ScriptControl to stop any running in an orderly fashion. 
        '''
        self._script_ctrl.stop()
