
import re
import wx
from .formsbase import FormSettings_Base

class FormSettings( FormSettings_Base ):

    @classmethod
    def show_modal( cls, parent, iniclass ):

        frm = cls(parent, iniclass)
        result = frm.ShowModal()

        frm.Destroy()

    def __init__( self, parent, iniclass ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param iniclass Class that inherits from happyscript.IniFile, which contains the settings to display.
        '''
        super().__init__(parent)

        self.iniclass = iniclass
        self.field_info = list()
        self.show_fields()


    def show_fields(self):

        self.Scroll.GetChildren()[0].Hide()

        scrollsizer = self.Scroll.GetSizer()

        count = 0

        for section_name in self.iniclass.sections():


            sbsizer = wx.StaticBoxSizer( wx.StaticBox( self.Scroll, wx.ID_ANY, section_name ), wx.VERTICAL )
            box = sbsizer.GetStaticBox()

            fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
            fgSizer1.AddGrowableCol( 1 )
            fgSizer1.SetFlexibleDirection( wx.BOTH )
            fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

            cfg = self.iniclass[section_name]
            for key, value in cfg.items():

                label = wx.StaticText( box, wx.ID_ANY, key, wx.DefaultPosition, wx.DefaultSize, 0 )
                label.Wrap( -1 )
                fgSizer1.Add( label, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

                txtCtrl = wx.TextCtrl( box, wx.ID_ANY, value, wx.DefaultPosition, wx.DefaultSize, 0 )
                fgSizer1.Add( txtCtrl, 5, wx.ALL|wx.EXPAND, 5 )

                self.field_info.append( (section_name, key, txtCtrl) )

            sbsizer.Add( fgSizer1, 1, wx.EXPAND, 5 )
            scrollsizer.Insert( count, sbsizer, 0, wx.EXPAND, 5 )
            count += 1



    def OnBtnApply( self, event ):

        msg = "OK to apply settings ?\n\n" \
              "They will be written to the following file:\n" \
             f"{self.iniclass._get_filename()}\n\n" \
              "You may have to restart the program for the changes to take effect."

        dlg = wx.MessageDialog(self, msg, "Happyscript", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            self.save_settings()
            self.EndModal(wx.ID_OK)

        dlg.Destroy()


    def OnBtnCancel( self, event ):
        self.EndModal(wx.ID_CANCEL)


    def save_settings(self):
        ''' Save the settings to the ini file.
            This is called when the user clicks the "Apply" button.
        '''
        cfg = self.iniclass._get_configparser()
        for section, key, txtCtrl in self.field_info:
            value = txtCtrl.GetValue()

            cfg.set(section, key, value)
            # print(f"Setting {section}.{key} = {value}")

        self.iniclass.write()
