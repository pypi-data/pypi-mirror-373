"""configuration.py"""
import configparser
from configparser import NoOptionError, NoSectionError

class ConfigurationManager:
    """
    Configuration Manager
    """

    def __init__(self, config_file):

        self.config_file = config_file
        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.config_file)

        except Exception as e:
            return None
        
    def get_config_value(self, section, option):
        """
        Get configuration value
        """
        try:
            return self.config.get(section, option)
        except (NoOptionError, NoSectionError):
            return None