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


def normalize(x, xmin, xmax):
    """Normalize a number to a 0-1 range given a min and max of its set."""
    return float(x - xmin) / float(xmax - xmin)


def get_scores(items):
    """Compute normalized scores (0-1) for commit numbers."""
    vals = [i["count"] for i in items]
    vals.append(0)

    xmin = min(vals)
    xmax = max(vals)

    # Normalize.
    for i in items:
        i["score"] = normalize(i["count"], xmin, xmax)

    return items
