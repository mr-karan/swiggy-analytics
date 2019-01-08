import os
import sys
from exceptions import SwiggyCliQuitError, SwiggyCliAuthError, SwiggyCliConfigError
from prompt_toolkit.shortcuts import ProgressBar
import requests

from cli import get_input_value, quit_prompt
from utils import save_config, get_config
from constants import SWIGGY_LOGIN_URL, SWIGGY_ORDER_URL, SWIGGY_URL

session = requests.Session()


def fetch_orders(order_id):
    orders = session.get(SWIGGY_ORDER_URL + '?order_id=' + str(offset_id))
    return orders


def initial_setup_prompt():
    """
    Prompt shown for the first time setup
    or when configure flag is passed.
    Fetch the keys from user and store in config file
    """
    try:
        swiggy_username = get_input_value(title='First time setup',
                                          text='Please enter your swiggy username')
    except SwiggyCliQuitError:
        sys.exit("Bye")
    try:
        swiggy_password = get_input_value(
            title='First time setup',
            text='Please enter your swiggy password')
    except SwiggyCliQuitError:
        sys.exit("Bye")

    save_config(username=swiggy_username, password=swiggy_password)
    return None


def perform_login():
    establish_connection = session.get(SWIGGY_URL)
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

    if login_response.status_code != 200:
        raise SwiggyCliAuthError(
            "Login response non success %s", login_response.status_code)
    import pdb
    pdb.set_trace()


def get_orders():
    orders = session.get(SWIGGY_ORDER_URL)
    # get the last order_id to use as offset param for next order fetch call

    offset_id = orders.json()['data']['orders'][-1]['order_id']
    count = orders.json()['data']['total_orders']

    pages = ceil(count/10)
    limit = 0

    while limit != pages:
        orders = fetch_orders(offset_id)
        offset_id = orders.json()['data']['orders'][-1]['order_id']
        print(offset_id)
        time.sleep(15)
