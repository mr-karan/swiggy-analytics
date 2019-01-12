import os
import sys
import time
from exceptions import (SwiggyAPIError, SwiggyCliAuthError,
                        SwiggyCliConfigError, SwiggyCliQuitError,
                        SwiggyDBError)
from math import ceil

import requests
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import ProgressBar

from cli import get_input_value, quit_prompt
from constants import (PROGRESS_BAR_FORMATTER, PROGRESS_BAR_STYLE,
                       SWIGGY_API_CALL_INTERVAL, SWIGGY_LOGIN_URL,
                       SWIGGY_ORDER_URL, SWIGGY_URL)
from db import SwiggyDB
from utils import get_config, save_config

session = requests.Session()


def fetch_orders(offset_id):
    response = session.get(SWIGGY_ORDER_URL + '?order_id=' + str(offset_id))
    return response.json().get('data').get('orders', [])


def initial_setup_prompt():
    """
    Prompt shown for the first time setup
    or when configure flag is passed.
    Fetch the keys from user and store in config file
    """
    try:
        swiggy_username = get_input_value(title='First time setup',
                                          text='Please enter your swiggy username. You can use your mobile number')
    except SwiggyCliQuitError:
        sys.exit("Bye")
    try:
        swiggy_password = get_input_value(
            title='First time setup',
            text='Please enter your swiggy password',
            password=True)
    except SwiggyCliQuitError:
        sys.exit("Bye")

    save_config(username=swiggy_username, password=swiggy_password)
    return None


def perform_login():
    establish_connection = session.get(SWIGGY_URL)
    # This is the most ugliest parsing I have ever written. Don't @ me
    csrf_token = establish_connection.text.split("csrfToken")[1].split("=")[
        1].split(";")[0][2:-1]

    if not csrf_token:
        raise SwiggyCliAuthError("Unable to parse CSRF Token. Login failed")

    # fetch username, password from config
    try:
        username, password = get_config()
    except SwiggyCliConfigError as e:
        raise e
    login_response = session.post(SWIGGY_LOGIN_URL, headers={'content-type': 'application/json'}, json={
                                  "mobile": username, "password": password, '_csrf': csrf_token})

    if login_response.text == "Invalid Request":
        perform_login()

    if login_response.status_code != 200:
        raise SwiggyCliAuthError(
            "Login response non success %s", login_response.status_code)


def get_orders(db):
    response = session.get(SWIGGY_ORDER_URL)
    if not response.json().get('data', None):
        raise SwiggyAPIError("Unable to fetch orders")

    # get the last order_id to use as offset param for next order fetch call
    orders = response.json().get('data').get('orders', None)
    if not orders:
        raise SwiggyAPIError("Unable to fetch orders")
    offset_id = orders[-1]['order_id']
    count = response.json().get('data')['total_orders']
    pages = ceil(count/10)

    label = "Fetching {} orders".format(count)

    with ProgressBar(style=PROGRESS_BAR_STYLE, formatters=PROGRESS_BAR_FORMATTER) as pb:
        for i in pb(range(pages), label=label):
            orders = fetch_orders(offset_id)
            if len(orders) == 0:
                break
            offset_id = orders[-1]['order_id']
            # swiggy super transaction wont have restaurant name
            try:
                db.insert_orders([(orders[i]['order_id'], orders[i]['order_total'],
                                   orders[i].get('restaurant_name', ''), orders[i]['order_time'],) for i in range(len(orders))])
            except SwiggyDBError as e:
                print(e)
            time.sleep(SWIGGY_API_CALL_INTERVAL)
