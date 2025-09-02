#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object for some flow control during a script
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

class ScriptUserAbortException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ScriptRecursiveAbortException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
