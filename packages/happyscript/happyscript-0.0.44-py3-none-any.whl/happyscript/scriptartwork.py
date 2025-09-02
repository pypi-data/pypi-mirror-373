
import wx, os
from .imglib import all_images

class ScriptArtwork(wx.ArtProvider):

    baseDir = None                                      # base directory with the artwork files
    
    overrides = { "wxART_QUIT":"exit.png",
                  "settings":"settings.png",
                  "user":"user_female_32.png",
                  "python":"python.png",
                  "scriptlist":"ScriptList.png",
                  "messages":"MessageList.png",
                  "logging":"Logging.png",
                  "tests":"TestList.png",
                  "charts":"charts.png",
                  
                  "test_fail":"TestFail.png",
                  "test_pass":"TestOK.png",
                  "test_todo":"Dash.png",
                  "test_warning":"TestWarning.png",
                  "test_idle":"TestIdle.png",
                  "test_running":"TestRunning.png",
                  "test_pause":"TestPause.png",
                  "script_list":"ScriptList.png",
                  "layout_DD":"Layout_DD.png",
                  "user_operator":"UserOperator.png",
                  "user_expert":"UserExpert.png",
                  "user_engineer":"UserEngineer.png",
                  "user_technician":"UserTechnician.png",
                  "reset":"reset.png",
                  "control_panel":"controls.png", 
                  "red_dot":"red_dot.png", 
                  "red_square":"red_square.png", 
                  "play":"play.png", 
                  "skip":"skip.png", 
                  "idle":"idle.png", 
                  "disable":"disable.png", 
                                    }
    
    @staticmethod
    def register():
        ''' Registers the artwork provider to wx.ArtProvider.
            baseDir is used as a flag so that we only do this once    
        '''
        if ScriptArtwork.baseDir is None:
            ScriptArtwork.baseDir = os.path.join(os.path.dirname(__file__), "artwork")
            wx.ArtProvider.Push(ScriptArtwork())

#     def CreateBitmap(self, _id, client, size):
#         ''' Returns bitmap if the 'id' matches a filename present in the artwork directory.
#             Otherwise returns none, so the next artwork provider will be called.
#         '''
#         if _id in self.overrides:
#             _id = self.overrides[_id]
#         
#         fname = os.path.join(ScriptArtwork.baseDir, _id)
#         if os.path.isfile(fname):
#             return wx.Bitmap( fname, )
#         print("%s not found" % str(_id))

    def CreateBitmap(self, _id, client, size):
        ''' Returns bitmap if the 'id' matches a filename present in the artwork directory.
            Otherwise returns none, so the next artwork provider will be called.
        '''
        if _id in self.overrides:
            _id = self.overrides[_id]
        
        if _id in all_images:
            img = all_images[_id].GetImage()
            return img.ConvertToBitmap()
        
        return wx.NullBitmap

