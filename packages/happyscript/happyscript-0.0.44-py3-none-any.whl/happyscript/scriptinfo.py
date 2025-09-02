#   ____       _    _                                     
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Object to manage test information
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2020   | Project : -
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 4/2/2021
#__________________________________________________|_________________________________________________________

import logging, os, time

class ScriptInfo(object):
    ''' Maintains test information and writes it to disk
    '''
    logger = logging.getLogger('happyscript')

    def __init__(self, testlist, use_yaml:bool):
        ''' Constructor
            @param testlist    object maintaining a list of all production tests
            @param use_yaml    Use yaml to write info file ?
        '''
        self.clear()
        self.__dict__["xx_testlist"] = testlist
        self.__dict__["xx_use_yaml"] = use_yaml
        
    def clear(self):
        ''' Clears all information
        '''
        self.__dict__["xx_info"] = dict()
        self.__dict__["xx_serials"] = list()
        self.__dict__["xx_filename"] = None
        self.__dict__["xx_dirty"] = False
        self.__dict__["xx_lastupdate"] = time.time()
                
    def set_serials(self, serials):
        ''' Set the serials from a given list.
            Any previously set serials will be deleted.
        '''
        self.xx_serials.clear()        
        if serials is not None:
            for sn in serials:
                self.add_serial(sn)
                
    def add_serial(self, *serials):
        ''' Add one or more serial numbers.
        '''        
        for serial in serials:
            if isinstance(serial, str):
                self.xx_serials.append(serial.strip() )
            else:
                self.logger.error("Given serial is invalid : '%s'" % str(serial) )
                self.xx_serials.append("")
            self.xx_dirty = True
            
            self.update_file()

    def set_filename(self, fname):
        ''' Sets the filename to write the data to.
            Set to 'None" to prevent writing the data
        '''
        self.xx_filename = fname
        self.xx_dirty = True
                
    def write_file(self, fname = None):
        ''' Write all the information to a text file.
            If no filename is given, the filename specified with set_filename() will be used.
            If it is None, data will not be written.
        '''
        if fname is None:
            fname = self.xx_filename
        if fname is None:
            return
        
        if self.xx_use_yaml:
            import yaml
            fname = os.path.splitext(fname)[0] + ".yml"
    
            with open(fname, "w") as file:
            
                if len(self.serials)>0:
                    serials_dict = { 'serials': self.serials }
                    yaml.dump(serials_dict, file)
                    
                if len(self.xx_info)>0:
                    yaml.dump(self.xx_info, file)
                
        else:
            import json
            fname = os.path.splitext(fname)[0] + ".json"
    
            with open(fname, "w", encoding="utf-8") as file:
            
                if len(self.serials)>0 and len(self.xx_info)>0:         # both serials and info
                    self.xx_info["serials"] = self.serials
                    json.dump(self.xx_info, file, ensure_ascii=False, indent=4)
                    del self.xx_info["serials"]
                    
                elif len(self.serials)>0:                               # only serials
                    serials_dict = { 'serials': self.serials }
                    json.dump(serials_dict, file, ensure_ascii=False, indent=4)
                    
                elif len(self.xx_info)>0:                               # only info
                    json.dump(self.xx_info, file, ensure_ascii=False, indent=4)

    def update_file(self, force=False):
        ''' Writes the output file when there have been changes, and last update has been some time (2s).
            @param   force    Force writing the file, even if there were no changes
        '''
        if len(self.xx_info)==0 and len(self.serials)==0:
            return
        
        t = time.time()
        if force or (self.xx_dirty and (t - self.xx_lastupdate > 2)):
            self.xx_dirty = False
            self.xx_lastupdate = t
            self.write_file()
                
    @property
    def serials(self):
        return self.xx_serials.copy()
                                
    def __getattr__(self, attr):
        ''' Called when value of NON-EXISTENT member is requested
        '''
        if attr.lower() in self.xx_info:
            return self.xx_info[attr.lower()]
        else:
            return None

    def __setattr__(self, attr, value):
        ''' Called for EVERY member assignment.
            If attribute does not exist yet, it is added to the info.
        ''' 
        if attr in self.__dict__:                       # is ordinary member of this class
            super().__setattr__(attr, value)
        elif attr.lower() in self.__dict__:
            super().__setattr__(attr.lower(), value)
        else:                                           # new value ? add to the list of info
            self.add(attr, value)

    def get_passed_tests(self, include = None, exclude = None):
        ''' Return a list of all production tests that passed.
            @param include    optional, list of test to include, other will be disregarded
            @param exclude    optional, list of tests to exclude
        '''
        if self.xx_testlist is None:
            return list()
        return self.xx_testlist.get_tests(True, include, exclude)
        
    def get_failed_tests(self, include = None, exclude = None):
        ''' Return a list of all production tests that failed or didn't execute.
            @param include    optional, list of test to include, other will be disregarded
            @param exclude    optional, list of tests to exclude
        '''
        if self.xx_testlist is None:
            return list() if include is None else include
        return self.xx_testlist.get_tests(False, include, exclude)
    
    def add(self, objName, theObject):
        ''' Add a a piece of information under the specified name.
            Is called when you assign a value to a non-existent property.
            File is written to disk from time to time.
        '''
        if not isinstance(objName, str) or not objName.isidentifier():
            self.logger.error("Given name for information is not a valid identifier : '%s'" % str(objName) )
            return

        self.xx_dirty = True
        objName = objName.lower().strip()        
        self.xx_info[objName] = theObject
        
        self.update_file()
