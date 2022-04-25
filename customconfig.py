"""
CustomConfig
"""

import configparser

class CustomConfig(configparser.ConfigParser):
    """
    Modified ConfigParser to properly interpret the data of my config
    """

    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self.storage = {"discord": {}}

    def read(self, filenames: str, encoding: str = None):
        """
        Modified read methos to process values returned in the config instead of doing it later
        """
        configparser.ConfigParser.read(self, filenames, encoding)
        self.storage["discord"]["guild"] = int(self["discord"]["guild"])
        self.storage["discord"]["blocklist"] = map(
            int, str.split(self["discord"]["blocklist"], ",")
        )
        self.storage["discord"]["moderator_role"] = int(self["discord"]["moderator_role"])
