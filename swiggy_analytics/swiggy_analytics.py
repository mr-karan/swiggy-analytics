
#!/usr/bin/python

"""
swiggy-cli-expense is a utility to fetch your orders
history from Swiggy and provide basic stats on them.

Author: Karan Sharma, https://mrkaran.dev

Licensed under the MIT License.
"""

import argparse
import os
import sys

from swiggy_analytics.cli import user_continue
from swiggy_analytics.constants import DB_FILEPATH
from swiggy_analytics.db import SwiggyDB
from swiggy_analytics.exceptions import (SwiggyAPIError, SwiggyCliAuthError,
                                         SwiggyCliConfigError)
from swiggy_analytics.helper import (display_stats, fetch_and_store_orders,
                                     initial_setup_prompt, perform_login)
from swiggy_analytics.utils import config_file_present


def main():
    parser = argparse.ArgumentParser(
        description="Fetch your past swiggy orders " +
                    "using the command line",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--configure', action='store_true',
                        help="Configure  swiggy-analytics  CLI  options. On running this command, " +
                        "you will be prompted for configuration values such as your Swiggy Username " +
                        "and an OTP sent to your registered mobile number. " +
                        "(the default location is ~/.aws/config). The AWS CLI will create/overwrite " +
                        "a configuration file for you, at ~/.swiggy-exepnse-config. \n" +

                        "Note: If you are not comfortable sharing your username with the utility, " +
                        "you can audit the code yourself. This file will only live in your filesystem and " +
                        "accessible by your username only. "
                        )
    parser.add_argument('--save', action='store_true',
                        help="Use this flag if you want to store your orders " +
                        "in a sqllite db file. After the program has completed the " +
                        "fetching orders, `swiggy.db` file wile be created in you current working directory. ")

    args = parser.parse_args()

    print('''Welcome to swiggy-analytics.

This command line tool will help you fetch your order history from https://swiggy.com.
You can choose to persist the detailed order information in a SQLite database or
perform lightweight stats operations using in-memory calculations.
''')
    if not config_file_present() or args.configure:
        initial_setup_prompt()

    if os.path.exists(DB_FILEPATH) and user_continue():
        db = SwiggyDB()
        # connect to the existing db
        db.init_db(persist=True)
        # show basic stats by fetching the results from already existing db
        display_stats(db)
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
        orders = fetch_and_store_orders(db)
    except SwiggyAPIError:
        sys.exit(
            "Error fetching orders from Swiggy. " +
            "Please check your credentials. " +
            "You can use swiggy-analytics --configure to regenerate")

    display_stats(db)

    return None


if __name__ == "__main__":
    sys.exit(main())
