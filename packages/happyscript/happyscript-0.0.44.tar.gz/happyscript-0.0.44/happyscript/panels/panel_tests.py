#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Panel with treeview of scrips
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : Oce BE-Board
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 5/2/2020
#__________________________________________________|_________________________________________________________

import logging
from enum import Enum, IntEnum
import wx

from .panelsbase import PanelTests_Base
from ..scriptartwork import ScriptArtwork
from ..forms.form_ontestfailure import FormOnTestFailure

class RunState(Enum):
    IDLE = 1
    RUN_SINGLE = 2
    RUNNING = 3
    PAUSED = 4
    FINISHED = 5
    DO_SETUP_FUNC = 6
    DO_CLEANUP_FUNC = 7
    WAIT_TEST_END = 8
    ERROR = 9
    START_FIRST = 10
    
class RunAction(Enum):
    NONE = 1
    STOP_ALL = 2
    PAUSE = 6


class TestIcon(IntEnum):
    FAIL = 0
    PASS = 1
    TODO = 2
    WARN = 3
    IDLE = 4
    RUNNING = 5
    PAUSED = 6

    @classmethod
    def GetImageList(cls):
        il = wx.ImageList(16, 16)                            # create imagelist with images for testlist
        il.Add( wx.ArtProvider.GetBitmap("test_fail") )
        il.Add( wx.ArtProvider.GetBitmap("test_pass") )
        il.Add( wx.ArtProvider.GetBitmap("test_todo") )
        il.Add( wx.ArtProvider.GetBitmap("test_warning" ))
        il.Add( wx.ArtProvider.GetBitmap("test_idle" ))
        il.Add( wx.ArtProvider.GetBitmap("test_running"))
        il.Add( wx.ArtProvider.GetBitmap("test_pause"))
        return il    

class TestInfo:
    ''' Structure to maintain information about a test.
    '''
    
    def __init__(self, description, scriptname, **args):
        self.description = description
        self.scriptname = scriptname
        self.extra_args = args
        self.passed = False

class PanelTests( PanelTests_Base):
    ''' Panel containing a treeview of all scripts in a given directory.
    '''
    logger = logging.getLogger("happyscript")

    def __init__( self, parent, mngr:'ScriptManager' ):
        ''' @param parent   Control to put this panel in.  Typically a notebook.
            @param mngr     The script manager
        '''
        PanelTests_Base.__init__(self, parent)
       
        self.on_sequence_start_callback = None
        self.on_sequence_end_callback = None
        
        self.mngr = mngr
       
        self.__run_state = RunState.IDLE
        self.__run_action = RunAction.NONE
        self.__testnum = -1

        self.tests = list()

        self.init_list()

    def init_list(self):
        ''' Initialize the list with tests to execute.
        '''
        ScriptArtwork.register()

        self.il = TestIcon.GetImageList() 
        self.m_lstTests.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        self.m_lstTests.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))

        info = wx.ListItem()                                                        # create columns
        info.Mask = wx.LIST_MASK_IMAGE
        info.Image = -1
        info.Align = wx.LIST_FORMAT_LEFT
        info.Text = ""
        self.m_lstTests.InsertColumn(0, info)

        info.Align = wx.LIST_FORMAT_LEFT
        info.Text = "Name"
        self.m_lstTests.InsertColumn(1, info)

        info.Mask = wx.LIST_MASK_IMAGE
        info.Image = -1
        info.Align = wx.LIST_FORMAT_LEFT
        info.Text = "?"
        self.m_lstTests.InsertColumn(2, info)
        
        self.m_lstTests.SetColumnWidth(0, 50)                                  # set initial column width
        self.m_lstTests.SetColumnWidth(1, 100)
        self.m_lstTests.SetColumnWidth(2, 50)
        
#         self.m_lstTests.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL,wx.NORMAL))
    
    def OnListSize( self, event ):
        ''' Adjust column width when form size changes.
        '''
        width = self.GetClientSize().width
        if width<160:
            width = 160;
        self.m_lstTests.SetColumnWidth(1, width-110)    
        event.Skip()
    
    def OnListRightClick( self, event ):
        self.selected_row = event.Index
        print( self.selected_row )
        pos = wx.GetMousePosition()
        pos = self.ScreenToClient( pos ) 
        self.PopupMenu( self.m_mnuTestList, pos  )
        
        
    
    def add_test(self, description, scriptname, **args):
        ''' Add a single test to the test list.
            @param description    Name to appear in test list
            @param scriptname     dot-notation of test
            @param args           optional arguments to be given to test 
        '''
        test = TestInfo(description, scriptname, **args)                    # object to keep state of test        
        self.tests.append(test)
        
        self.m_lstTests.Append( ('', description, '') )                     # add fields to table        
        cnt = self.m_lstTests.GetItemCount()
        self.m_lstTests.SetItem(cnt-1, 0, "", imageId=TestIcon.IDLE )
        self.m_lstTests.SetItem(cnt-1, 2, "", imageId=TestIcon.TODO )

    def get_tests(self, is_passed, include = None, exclude = None):
        ''' Get list of tests that have passed or have not (yet) passed.
            
            @param is_passed  True to get list of passed tests, False for failed or not executed
            @param include    optional, list of test to include, other will be disregarded
            @param exclude    optional, list of tests to exclude
        '''
        result = list()
        for i in range(len(self.tests)):
            if (i==self.__testnum) or (self.tests[i].passed!=is_passed):    # active test, or doesn't match 
                continue

            if (exclude is not None) and (self.tests[i].description in exclude): # must it be excluded ?
                continue
            
            if (include is None) or (self.tests[i].description in include):     # add if must be included 
                result.append(self.tests[i].description)
        return result

    def OnBtnStartClick( self, event ):
        self.state = RunState.START_FIRST

    def OnBtnPauseClick( self, event ):
        if self.state==RunState.PAUSED:                 # in pause -> run next test
            self.state = RunState.RUNNING
        else:
            self.__run_action = RunAction.PAUSE         # not in pause -> set pause flag

    def OnBtnStopClick( self, event ):
        self.__run_action = RunAction.STOP_ALL
        self.mngr.stop_scripts()                # stop script if running

    def reset_icons(self):
        ''' Set all the icons right for a new test run
        '''
        for index in range(len(self.tests)):
            self.m_lstTests.SetItem(index, 0, "", imageId=TestIcon.IDLE )
            self.m_lstTests.SetItem(index, 2, "", imageId=TestIcon.TODO )
            
            self.tests[index].passed = False

    @property
    def state(self):
        return self.__run_state
    
    @state.setter
    def state(self, value):
        ''' Sets the next state for the test state machine.
            Activates timer such that state will be executed.
            Also checks some state changes to see if they are valid
        '''
        if value==RunState.START_FIRST:
            self.__run_action = RunAction.NONE
            if self.state != RunState.IDLE:
                raise Exception("Test state is not idle, cannot start test sequence.")
        
        self.__run_state = value
        if value==RunState.IDLE:
            self.m_tmrStateMachine.Stop()
        else:
            self.m_tmrStateMachine.StartOnce(10)

    def OnTmrStateMachine( self, event ):

        if self.state == RunState.IDLE: # =============================================== I D L E   S T A T E 
            
            self.m_tmrStateMachine.Stop()
            
        elif self.state == RunState.START_FIRST: # ==================================== S T A R T   F I R S T

            self.__testnum = -1
            self.logger.debug("Starting new test sequence")
            self.m_txtStatus.Label = "Starting"
            self.m_txtStatus.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            self.m_lstTests.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )            
            self.m_lstTests.Refresh()

            self.reset_icons()
            
            self.m_btnStart.Enabled = False
            self.m_btnStop.Enabled = True
            
            self.state = RunState.DO_SETUP_FUNC

        elif self.state == RunState.DO_SETUP_FUNC:            # ===================== S E T U P     S T A T E

                if self.on_sequence_start_callback is None:                 # just start test if no callback
                    self.state = RunState.RUNNING                     
                else:
                    try:
                        result = self.on_sequence_start_callback()          # execute callback
                        
                        if isinstance(result, str):                         # callback returned error message
                            self.m_txtStatus.Label = result
                            self.state = RunState.ERROR
                        elif isinstance(result, bool) and result==False:    # callback returned False value
                            self.m_txtStatus.Label = "Test run aborted"
                            self.state = RunState.ERROR
                        else:                                               # all OK -> start tests
                            self.state = RunState.RUNNING

                    except Exception as e:
                        self.logger.critical("Error in callback at beginning of test", exc_info=e)
                        self.m_txtStatus.Label = "Internal error #1"
                        self.state = RunState.ERROR
                        return

        elif self.state == RunState.RUNNING:                  # ========================= R U N     S T A T E
            
            self.__testnum += 1                                             # go next test
            
            if self.__testnum >= len(self.tests):                           # all tests done
                self.logger.debug("No more test to execute")
                self.state = RunState.DO_CLEANUP_FUNC
            
            elif self.__run_action==RunAction.STOP_ALL:                     # user asked for stopping of tests
                self.__run_action = RunAction.NONE
                self.logger.debug("Stopping all tests")
                self.state = RunState.DO_CLEANUP_FUNC
            
            else:                                                           # going to next test
                
                self.m_lstTests.EnsureVisible(self.__testnum)               # icons to indicate test running
                self.m_lstTests.SetItem(self.__testnum, 0, "", imageId=TestIcon.RUNNING )
                self.m_lstTests.SetItem(self.__testnum, 2, "", imageId=TestIcon.TODO )
                self.m_lstTests.Update()
        
                self.m_txtStatus.Label = "Running test %d" % (self.__testnum+1)
                sname = self.tests[self.__testnum].scriptname               # get script name and params
                sargs = self.tests[self.__testnum].extra_args
                if sargs is None:                                           # execute script
                    self.mngr._script_runner.run_script(sname)
                else:
                    self.mngr._script_runner.run_script(sname, **sargs)
                
                self.state = RunState.WAIT_TEST_END

        elif self.state == RunState.WAIT_TEST_END: # ================ W A I T  T E S T   E N D  ==========

            if self.mngr._script_runner.busy:                           # script still busy
                self.state = RunState.WAIT_TEST_END                     # keep waiting

            else:                                                       # script is no longer busy
                test_pass = self.mngr._script_runner.test_passed
                index = self.__testnum

                if test_pass:
                    self.m_lstTests.SetItem(index, 0, "", imageId=TestIcon.IDLE )   # icons indicating test is done
                self.m_lstTests.SetItem(index, 2, "", imageId=TestIcon.PASS if test_pass else TestIcon.FAIL )
                self.m_lstTests.Update()
                
                self.tests[index].passed = test_pass                    # keep test result in test info
                
                if test_pass:
                    self.state = RunState.RUNNING                   # test passed, run next test
                else:
                    self.m_lstTests.SetItem(index, 0, "", imageId=TestIcon.WARN )
                    result = FormOnTestFailure.show(self.tests[index].description)      # ask what to do if test failed
                    
                    self.m_lstTests.SetItem(index, 0, "", imageId=TestIcon.IDLE )
        
                    if result==wx.ID_RETRY:                         # retry -> decrement test nr so that this one is repeated next
                        self.__testnum -= 1
                        self.logger.warn("Test failed, doing retry")
                        self.state = RunState.RUNNING
                    elif result==wx.ID_FORWARD:                     # skip test -> nothing special to do for this
                        self.logger.warn("Test skipped by user")
                        self.state = RunState.RUNNING
                    else:                                           # stop test -> set flag to stop
                        self.logger.warn("Test sequence aborted by user")
                        self.state = RunState.DO_CLEANUP_FUNC

        elif self.state == RunState.RUN_SINGLE:               # ================ S E T U P     S T A T E ==========
            
            self.logger.error("Run single not yet implemented")
            self.state = RunState.ERROR

        elif self.state == RunState.PAUSED:                   # ================ S E T U P     S T A T E ==========

            self.logger.error("Pause not yet implemented")
            self.state = RunState.ERROR

        elif self.state == RunState.DO_CLEANUP_FUNC:          # ================ C LE A N U P     S T A T E ==========            

            if self.on_sequence_end_callback is None:
                self.state = RunState.FINISHED
            else: 
                try:
                    self.on_sequence_end_callback()
                    self.state = RunState.FINISHED
                except Exception as e:
                    self.logger.critical("Error in callback at end of test", exc_info=e)
                    self.m_txtStatus.Label = "Internal error #2"
                    self.state = RunState.ERROR

        elif self.state == RunState.FINISHED:                 # ================ F I N I S H    S T A T E ==========
            
            self.logger.debug("Tests finished")
            
            num_fails = sum( 1 for x in self.tests if not x.passed)
            
            if num_fails==0:
                self.m_txtStatus.Label = "All test OK"
                self.m_txtStatus.SetForegroundColour(wx.Colour( 0, 128, 0 ))
                self.m_lstTests.SetBackgroundColour( wx.Colour( 226, 239, 217 ) )
            elif num_fails==1:
                self.m_txtStatus.Label = "1 test failed !"
                self.m_txtStatus.SetForegroundColour(wx.RED)
                self.m_lstTests.SetBackgroundColour( wx.Colour( 255, 201, 201 ) )
            else:
                self.m_txtStatus.Label = "%d tests failed !" % num_fails
                self.m_txtStatus.SetForegroundColour(wx.RED)
                self.m_lstTests.SetBackgroundColour( wx.Colour( 255, 201, 201 ) )

            self.m_lstTests.Refresh()

            self.state = RunState.IDLE
            self.m_btnStart.Enabled = True
            self.m_btnStop.Enabled = False

        elif self.state == RunState.ERROR:                    # ================ E R R O R  S T A T E ==========
            
            self.state = RunState.IDLE
            self.m_btnStart.Enabled = True
            self.m_btnStop.Enabled = False
        
        else:                                                       # ================ I N V A L I D    S T A T E ==========
            self.logger.critical("run_state invalid in testlist state machine")
            self.m_txtStatus = "Internal error #3"

            self.state = RunState.IDLE
            self.m_btnStart.Enabled = True
            self.m_btnStop.Enabled = False




