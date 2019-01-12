import argparse
import logging
import os
import string
import sys
import time
from exceptions import SwiggyCliAuthError, SwiggyCliConfigError, SwiggyAPIError
from functools import lru_cache
from math import ceil

from db import SwiggyDB
import requests
from prompt_toolkit import prompt

from helper import get_orders, initial_setup_prompt, perform_login
from utils import config_file_present


def main():
    parser = argparse.ArgumentParser(
        description="Fetch your past swiggy orders " +
                    "using the command line",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--configure', action='store_true',
                        help="Configure  Swiggy-Expense  CLI  options. On running this command, " +
                        "you will be prompted for configuration values such as your Swiggy Username " +
                        "and your Swiggy Password. " +
                        "(the default location is ~/.aws/config). The AWS CLI will create/overwrite " +
                        "a configuration file for you, at ~/.swiggy-exepnse-config. \n" +

                        "Note: If you are not comfortable sharing your username and password with the utility, " +
                        "you can audit the code yourself. This file will only live in your filesystem and " +
                        "accessible by your username only. "
                        )
    args = parser.parse_args()

    print('''Welcome to swiggy-expense.

This command line tool will help you fetch your order history from https://swiggy.com.
You can choose to persist the detailed order information in a SQLite database or
perform lightweight stats operations using in-memory calculations.
''')
    if not config_file_present() or args.configure:
        initial_setup_prompt()

    db = SwiggyDB()
    db.init_db()

    try:
        perform_login()
    except SwiggyCliConfigError:
        sys.exit(
            "Error reading config file. Please generate a config file using --configure flag.")
    except SwiggyCliAuthError:
        sys.exit("Login to swiggy failed.")

    try:
        orders = get_orders()
    except SwiggyAPIError:
        sys.exit(
            "Error fetching orders from Swiggy. " +
            "Please check your credentials. " +
            "You can use swiggy-expense --configure to regenerate")
    return None


if __name__ == "__main__":
    sys.exit(main())
