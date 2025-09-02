#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Background form to stop a running script
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Happyscript
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 30/11/2023
#__________________________________________________|_________________________________________________________


from .formsbase import FormStop_base

class FormStop( FormStop_base):
    ''' Form for asking the operator to select something from a list
    '''

    def __init__( self, message, mngr ):
        ''' constructor
        '''
        super().__init__(mngr.dialog)
        
        self._mngr = mngr
        self.m_lblMessage.Label = message                   # show the text message

    def OnBtnStop( self, event ):
        self._mngr.stop_scripts()
        self.Close()

    def update_message(self, msg):
        ''' Update the message that is shown.
        '''
        self.m_lblMessage.Label = msg