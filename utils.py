import configparser

from constants import CONFIG_FILEPATH
import os


def save_config(username, password):
    Config = configparser.ConfigParser()
    with open(CONFIG_FILEPATH, 'w') as config_file:
        # add the settings to the structure of the file, and lets write it out...
        Config.add_section('Auth')
        Config.set('Auth', 'Username', username)
        Config.set('Auth', 'Password', password)
        Config.write(config_file)


def get_config():
    if not config_file_present():
        raise SwiggyCliConfigError("No config file present")

    Config = configparser.ConfigParser()
    Config.read(CONFIG_FILEPATH)
    return Config.get('Auth', 'Username'), Config.get('Auth', 'Password')


def config_file_present():
    return os.path.exists(os.path.join(CONFIG_FILEPATH))
