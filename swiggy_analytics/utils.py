import calendar
import configparser
import os
from datetime import datetime

from swiggy_analytics.constants import CONFIG_FILEPATH



def save_config(username):
    """
    Saves a config file to the user's specified location.
    """
    Config = configparser.RawConfigParser()
    with open(CONFIG_FILEPATH, 'w') as config_file:
        # add the settings to the structure of the file, and lets write it out...
        Config.add_section('Auth')
        Config.set('Auth', 'Username', username)
        Config.write(config_file)


def get_config():
    """
    Returns the user's credentials from the config if it exists.
    """
    if not config_file_present():
        raise SwiggyCliConfigError("No config file present")

    Config = configparser.RawConfigParser()
    Config.read(CONFIG_FILEPATH)
    return Config.get('Auth', 'Username')


def config_file_present():
    """
    Checks whether the config file exists or not.
    """
    return os.path.exists(os.path.join(CONFIG_FILEPATH))


def normalize(x, xmin, xmax):
    """Normalize a number to a 0-1 range given a min and max of its set."""
    return float(x - xmin) / float(xmax - xmin)


def get_scores(items):
    """Compute normalized scores (0-1) for order count."""
    vals = [i["count"] for i in items]
    vals.append(0)

    xmin = min(vals)
    xmax = max(vals)

    # Normalize.
    for i in items:
        i["score"] = normalize(i["count"], xmin, xmax)

    return items


def get_weekday_name(int_day):
    """
    Returns name of the day based on it's int representation (eg Sunday=0, Monday=1).
    """
    return calendar.day_name[int_day-1]


def get_month(date):
    """
    Converts string representation of date in form of 2018-11-10 as Nov-18
    """
    return datetime.strptime(date, '%Y-%m-%d').strftime('%b-%y')


def format_amount(data):
    """
    Prefixes the amount with the rupee symbol.
    """
    return "₹"+str(data)
