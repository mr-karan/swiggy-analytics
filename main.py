
#!/usr/bin/python

"""
swiggy-cli-expense is a utility to fetch your orders
history from Swiggy and provide basic stats on them.

Author: Karan Sharma, http://mrkaran.com

Licensed under the MIT License.
"""

import argparse
import logging
import os
import string
import sys
import time
from exceptions import SwiggyAPIError, SwiggyCliAuthError, SwiggyCliConfigError
from functools import lru_cache
from math import ceil

import requests
from prompt_toolkit import prompt

from db import SwiggyDB
from helper import get_orders, initial_setup_prompt, perform_login, display_stats
from utils import config_file_present
from cli import print_bars, user_continue
from constants import DB_FILEPATH


def main():
    # return print_bars()

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
    parser.add_argument('--save', action='store_true',
                        help="Use this flag if you want to store your orders " +
                        "in a sqllite db file. After the program has completed the " +
                        "fetching orders, `swiggy.db` file wile be created in you current working directory. ")

    args = parser.parse_args()

    print('''Welcome to swiggy-expense.

This command line tool will help you fetch your order history from https://swiggy.com.
You can choose to persist the detailed order information in a SQLite database or
perform lightweight stats operations using in-memory calculations.
''')
    if not config_file_present() or args.configure:
        initial_setup_prompt()

    if os.path.exists(DB_FILEPATH) and user_continue():
        db = SwiggyDB()
        db.init_db(persist=True)
        ans = display_stats(db)
        print(ans)
        return None

    db = SwiggyDB()
    db.init_db(persist=args.save)
    db.create_db()

    try:
        perform_login()
    except SwiggyCliConfigError:
        sys.exit(
            "Error reading config file. Please generate a config file using --configure flag.")
    except SwiggyCliAuthError:
        sys.exit("Login to swiggy failed.")

    try:
        orders = get_orders(db)
    except SwiggyAPIError:
        sys.exit(
            "Error fetching orders from Swiggy. " +
            "Please check your credentials. " +
            "You can use swiggy-expense --configure to regenerate")

    # if not args.save:
    display_stats(db)

    return None


if __name__ == "__main__":
    sys.exit(main())
