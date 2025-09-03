from __future__ import annotations
import configparser as cp
import os
import platform
import re
from typing import *

VALID_SEMESTER = Literal['fall', 'summer', 'winter']
DATA_FILE = "preferences.ini"
APP_DATA_PATH = None


class Preferences:
    def __init__(self):
        self._config: cp.ConfigParser = _read_ini()
        pass

    # ---------------------------------------------------------------------------------------------
    # directories
    # ---------------------------------------------------------------------------------------------
    def home_directory(self):
        """the users home directory, used to find the default place to save documents
        MAC:        $HOME
        WINDOWS:    %CSIDL_MYDOCUMENTS% or "~/Documents"
        """
        operating_system = platform.system().lower()

        user_base_dir = None
        if re.match(r'win', operating_system):
            user_base_dir = os.environ.get('CSIDL_MYDOCUMENTS', None)
            if user_base_dir is None:
                user_base_dir = os.path.expanduser("~/Documents")
        elif re.match(r'darwin|posix', operating_system):
            user_base_dir = os.environ['HOME']
        if user_base_dir is not None and os.path.isdir(user_base_dir):
            return user_base_dir
        return None

    def previous_file(self, file: Optional[str] = None) -> Optional[str]:
        """saves the filename last used for the specified semester"""
        if 'MOST_RECENT' not in self._config:
            self._config['MOST_RECENT'] = {}

        if file is not None and os.path.isfile(file):
            directory = os.path.dirname(os.path.realpath(file))
            filename = os.path.basename(file)
            if self.semester() == 'fall':
                self._config['MOST_RECENT']['fall_directory'] = directory
                self._config['MOST_RECENT']['fall_last_file'] = filename
            elif self.semester() == 'winter':
                self._config['MOST_RECENT']['winter_directory'] = directory
                self._config['MOST_RECENT']['winter_last_file'] = filename
            elif self.semester() == 'summer':
                self._config['MOST_RECENT']['summer_directory'] = directory
                self._config['MOST_RECENT']['summer_last_file'] = filename
            else:
                self._config['MOST_RECENT']['fall_directory'] = directory
                self._config['MOST_RECENT']['fall_last_file'] = filename

        else:
            if self.semester() == 'fall':
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
                filename = self._config['MOST_RECENT'].get('fall_last_file', None)
            elif self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('winter_directory', None)
                filename = self._config['MOST_RECENT'].get('winter_last_file', None)
            elif self.semester() == 'summer':
                directory = self._config['MOST_RECENT'].get('summer_directory', None)
                filename = self._config['MOST_RECENT'].get('summer_last_file', None)
            else:
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
                filename = self._config['MOST_RECENT'].get('fall_last_file', None)

        if directory is not None and filename is not None:
            if os.path.isfile(directory + "/" + filename):
                y = os.path.realpath(directory + "/" + filename)
                return os.path.realpath(directory + "/" + filename)
        return None

    def current_dir(self, new_dir: Optional[str] = None) -> Optional[str]:
        """what was the last directory used to save or read a file?"""
        if 'MOST_RECENT' not in self._config:
            self._config['MOST_RECENT'] = {}

        directory = None

        if new_dir is not None and os.path.isdir(new_dir):
            directory = os.path.dirname(os.path.dirname(os.path.realpath(new_dir)))
            if self.semester() == 'fall':
                self._config['MOST_RECENT']['fall_directory'] = directory
            elif self.semester() == 'winter':
                self._config['MOST_RECENT']['winter_directory'] = directory
            elif self.semester() == 'summer':
                self._config['MOST_RECENT']['summer_directory'] = directory

        else:
            if self.semester() == 'fall':
                directory = self._config['MOST_RECENT'].get('fall_directory', None)
            if self.semester() == 'winter':
                directory = self._config['MOST_RECENT'].get('winter_directory', None)
            if self.semester() == 'summer':
                directory = self._config['MOST_RECENT'].get('summer_directory', None)

        if directory is not None:
            if os.path.isdir(directory):
                return os.path.realpath(directory)
        return None


    # ---------------------------------------------------------------------------------------------
    # look and feel
    # ---------------------------------------------------------------------------------------------
    def _set_default_theme(self):
        """set up default themes based on OS
        MAC:        'aqua', no dark mode (tk picks up on dark mode settings)
        WINDOWS:    'winnative', no dark mode (unfortunately, tk does NOT pick up on dark mode settings)
        """
        operating_system = platform.system().lower()
        if re.match(r'win', operating_system):
            self._config['COLOURS']['theme'] = "winnative"
        elif re.match(r'darwin|posix', operating_system):
            self._config['COLOURS']['theme'] = "aqua"
        else:
            self._config['COLOURS']['theme'] = "classic"

    def available_themes(self) -> tuple[str,...]:
        return 'aqua', 'clam', 'alt', 'default', 'classic', 'winnative'

    def theme(self, theme: str = None) -> str:
        """set the theme"""
        if 'COLOURS' not in self._config or 'theme' not in self._config['COLOURS']:
            self._set_default_theme()

        operating_system = platform.system().lower()

        # theme was specified
        if theme is not None:

            # ignore if not in list
            if theme in self.available_themes():

                # don't set themes that don't go with the operating system
                if re.match(r'win', operating_system) and theme != "aqua":
                    self._config['COLOURS']['theme'] = theme
                elif re.match(r'darwin|posix', operating_system) and theme != "winnative":
                    self._config['COLOURS']['theme'] = theme
                elif theme != "aqua" and theme != 'winnative':
                    self._config['COLOURS']['theme'] = theme

        return self._config['COLOURS']['theme']

    def dark_mode(self, dark_mode: bool = None) -> bool:
        """dark mode is ignored if theme is either aqua or winnative"""

        if 'COLOURS' not in self._config or 'dark_mode' not in self._config['COLOURS']:
            self._config['COLOURS'] = {'dark_mode': '0'}

        if dark_mode is not None:
            self._config['COLOURS']['dark_mode'] = str(dark_mode)
        return self._config['COLOURS'].getboolean('dark_mode')

    def font_size(self, value: Optional[int] = None) -> int:
        """Specify the _normal_ font size"""

        operating_system = platform.system().lower()
        if 'FONT_SIZE' not in self._config:
            self._config['FONT_SIZE'] = {'windows':'13', 'darwin':'10'}


        if re.match(r'win', operating_system):
            if value is not None:
                self._config['FONT_SIZE']['windows'] = str(value)
            return int(self._config['FONT_SIZE'].get("windows", '10'))

        else:
            if value is not None:
                self._config['FONT_SIZE']['darwin'] = str(value)
            return int(self._config['FONT_SIZE'].get("darwin", '13'))

    # ---------------------------------------------------------------------------------------------
    # semester
    # ---------------------------------------------------------------------------------------------
    def semester(self, semester: VALID_SEMESTER = None) -> VALID_SEMESTER:
        if 'MOST_RECENT' not in self._config:
            self._config['MOST_RECENT'] = {'semester':'fall'}
        if semester is not None:
            self._config['MOST_RECENT']['semester'] = semester
        return self._config['MOST_RECENT'].get('semester', "fall")


    # ---------------------------------------------------------------------------------------------
    # auto save
    # ---------------------------------------------------------------------------------------------
    def auto_save(self, value: Optional[bool] = None) -> bool:
        if 'AUTO_SAVE' not in self._config:
            self._config['AUTO_SAVE'] = {'set':'1'}
        if value is not None:
            if value:
                self._config['AUTO_SAVE']['set'] = '1'
            else:
                self._config['AUTO_SAVE']['set'] = '0'

        if self._config['AUTO_SAVE']['set'] == '1':
            return True
        else:
            return False


    # ---------------------------------------------------------------------------------------------
    # save the current preferences
    # ---------------------------------------------------------------------------------------------
    def save(self):
        _write_ini(self._config)


def _read_ini() -> cp.ConfigParser:
    """if the ini file can be found, read it, if the config file cannot be found, use defaults"""
    ini_file = _get_app_data_location(DATA_FILE)
    config = cp.ConfigParser()

    # ini file exists, read it
    if ini_file and os.path.exists(ini_file):
        config.read(ini_file)
        return config

    # if ini file doesn't exist, create default info
    config['MOST_RECENT'] = {}

    config['MOST_RECENT']['fall_directory'] = ''
    config['MOST_RECENT']['fall_last_file'] = ''
    config['MOST_RECENT']['winter_directory'] = ''
    config['MOST_RECENT']['winter_file'] = ''
    config['MOST_RECENT']['summer_directory'] = ''
    config['MOST_RECENT']['summer_last_file'] = ''
    config['MOST_RECENT']['semester'] = 'fall'
    config['COLOURS'] = {}
    config['COLOURS']['dark_mode'] = "yes"
    config['AUTO_SAVE'] = {}
    config['AUTO_SAVE']['set'] = '1'
    config['FONT_SIZE'] = {}
    config['FONT_SIZE']['windows'] = '13'
    config['FONT_SIZE']['darwin'] = '10'
    return config


def _get_app_data_location(ini_file_name: str) -> Optional[str]:
    global APP_DATA_PATH
    if APP_DATA_PATH is not None:
        return APP_DATA_PATH
    operating_system = platform.system().lower()
    sub_dir = "scheduling_and_allocation"

    user_base_dir = None
    app_dir = None
    if re.match(r'win', operating_system):
        user_base_dir = os.environ['APPDATA'] if os.environ['AppData'] else os.environ['USERPROFILE']
        app_dir = os.path.join(user_base_dir, sub_dir)
    elif re.search('darwin', operating_system):
        user_base_dir = os.environ['HOME']
        app_dir = os.path.join(user_base_dir, "." + sub_dir)

    if not (app_dir and os.path.exists(app_dir)):
        try:
            os.mkdir(app_dir)
        except FileNotFoundError:
            return None

    ini_file = os.path.join(user_base_dir, app_dir, ini_file_name)
    APP_DATA_PATH = ini_file
    return ini_file


def _write_ini(config: cp.ConfigParser):
    """write _preferences in a safe place (it's secret, ha! ha!)"""
    ini_file = _get_app_data_location(DATA_FILE)
    if ini_file is None:
        return

    with open(ini_file, 'w') as configfile:
        config.write(configfile)
