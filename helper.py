import os
import sys
import time
from exceptions import (SwiggyCliAuthError, SwiggyCliConfigError,
                        SwiggyCliQuitError)
from math import ceil

import requests
from prompt_toolkit.shortcuts import ProgressBar

from cli import get_input_value, quit_prompt
from constants import SWIGGY_LOGIN_URL, SWIGGY_ORDER_URL, SWIGGY_URL
from utils import get_config, save_config
from db import insert_orders
session = requests.Session()


def fetch_orders(offset_id):
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


def get_orders():
    orders = session.get(SWIGGY_ORDER_URL)
    # get the last order_id to use as offset param for next order fetch call
    offset_id = orders.json()['data']['orders'][-1]['order_id']
    count = orders.json()['data']['total_orders']

    pages = ceil(count/10)
    limit = 0

    while limit != pages:
        orders = fetch_orders(offset_id)
        if len(orders) == 0:
            break
        orders_list = orders.json()['data']['orders']
        offset_id = orders_list[-1]['order_id']
        print(offset_id)
        # swiggy super transaction wont have restaurant name
        insert_orders([(orders_list[i]['order_id'], orders_list[i]['order_total'],
                        orders_list[i].get('restaurant_name', ''), orders_list[i]['order_time'],) for i in range(len(orders_list))])
        time.sleep(10)
