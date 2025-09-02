#   ____       _    _
#  |  _ \  ___| | _(_)_ __ ___   ___    Copyright  | Title   : Ini-file base class for happyscript 
#  | | | |/ _ \ |/ / | '_ ` _ \ / _ \   (c) 2023   | Project : n/a
#  | |_| |  __/   <| | | | | | | (_) |   Dekimo    | Authors : MVR
#  |____/ \___|_|\_\_|_| |_| |_|\___/   Products   | Created : 14/8/2025
#__________________________________________________|_________________________________________________________
#

import os, configparser

class IniFileMeta(type):
    def __getitem__(self, arg):
        ''' This method is called when the class is indexed with square brackets, e.g. IniFile['section_name'].
            'self' refers to the class itself, and 'arg' is the section name being requested.
        '''
        # print("__getitem__:", self, arg)
        return self.get_section(arg)

    def __contains__(self, arg):
        # print("__contains__:", self, arg)
        return self.has_section(arg)

class IniFile(metaclass=IniFileMeta):

    __configparser_object = None
    __filename = None

    @classmethod
    def read(cls, filename: str, /, generate_default: bool = True):
        ''' Read values from the given ini-file.
            Only sections and values that are present as inner classes of this class will be read.
            If the file does not exist, it can be created with default values.

            :param filename: The name of the ini-file to read.
            :param generate_default: If True, the file will be created with default values if it does not exist.
        '''

        inifile = configparser.ConfigParser()
        cls.__configparser_object = inifile                     # store the configparser object for later use

        filename = os.path.normpath(os.path.abspath(filename))  # get the absolute, normalized path to the file
        cls.__filename = filename                               # store the filename for later use

        file_exists = os.path.exists(filename)                  # check if the file exists and read it if it does
        if file_exists:
            inifile.read(filename)

        for section, attr in cls.dataclass_sections():          # go over all the sections defined in the class

            if inifile.has_section(section):                    # if section exists in the config file
                for field in attr.__dataclass_fields__:
                    if inifile.has_option(section, field):      # read our class values from the inifile if present
                        value = inifile.get(section, field)
                        if value is not None:
                            setattr(attr, field, value)
                    else:
                        value = getattr(attr, field)            # write our class value as default if not present in the inifile
                        inifile.set(section, field, str(value))

            else:                                               # if section does not exist, create it and copy the default values
                inifile.add_section(section)
                for field in attr.__dataclass_fields__:
                    value = getattr(attr, field)
                    if value is not None:                     # only write the field if it has a value
                        inifile.set(section, field, str(value))

        if not file_exists and generate_default:                # create the file with default values if it does not exist
            with open(filename, 'w') as f:
                inifile.write(f)

        from .staticscriptmanager import StaticScriptManager
        StaticScriptManager._set_ini(cls)                       # set the ini file class in the script manager

    @classmethod
    def _get_configparser(cls):
        ''' Returns the configparser object that was created by the read() method. '''
        return cls.__configparser_object

    @classmethod
    def _get_filename(cls):
        ''' Returns the filename of the ini file that was read by the read() method. '''
        return cls.__filename

    @classmethod
    def dataclass_sections(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, type) and hasattr(attr, "__dataclass_fields__"):
                yield attr_name, attr

    @classmethod
    def print_dataclass(cls):
        for section, attr in cls.dataclass_sections():
            print(f"{section}:")
            for field in attr.__dataclass_fields__:
                value = getattr(attr, field)
                print(f"* {field} = {value}")

    @classmethod
    def write(cls):
        ''' Write the current values to the ini-file.
            Any changes to the file will be lost.
            TODO: 
        '''
        assert cls._get_filename() is not None, "You must first read the settings from a file before doing a write().  " \
                                                "Note that you can do read() even if the file does not exist."

        config = cls._get_configparser() or configparser.ConfigParser()

        for section, attr in cls.dataclass_sections():
            if not config.has_section(section):
                config.add_section(section)

            for field in attr.__dataclass_fields__:
                if not config.has_option(section, field):
                    value = getattr(attr, field)
                    config.set(section, field, value)

        with open(cls._get_filename(), 'w') as configfile:
            config.write(configfile)

    @classmethod
    def get_section(cls, name:str):
        ''' returns a configparser section for the given name, or an empty section if the name is not found.       
        '''

        if cls.__configparser_object is not None and name in cls.__configparser_object.sections():
            ini = cls.__configparser_object
        else:
            ini = configparser.ConfigParser()
            ini.read_string(f"[{name}]\n\n")

        return ini[name]

    @classmethod
    def sections(cls):
        ''' Returns a list of all sections in the ini file. '''
        if cls.__configparser_object is not None:
            return cls.__configparser_object.sections()
        else:
            return []
        
    @classmethod
    def has_section(cls, section: str) -> bool:
        ''' Checks if the given section exists in the ini file. '''
        if cls.__configparser_object is not None:
            return cls.__configparser_object.has_section(section)
        return False

    @classmethod
    def has_option(cls, section: str, option: str) -> bool:
        ''' Checks if the given option exists in the given section of the ini file. '''
        if cls.__configparser_object is not None:
            return cls.__configparser_object.has_option(section, option)    
        return False
    
    @classmethod
    def set(cls, section: str, option: str, value: str):
        ''' Sets the value of the given option in the given section of the ini file. '''
        assert cls.__configparser_object is not None, "You must first read the settings from a file before doing a set()."

        cls.__configparser_object.set(section, option, str(value) )
        