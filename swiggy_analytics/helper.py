import os
import sys
import time
from collections import namedtuple
from math import ceil

import requests
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import ProgressBar

from swiggy_analytics.cli import get_input_value, print_bars, quit_prompt
from swiggy_analytics.constants import (PROGRESS_BAR_FORMATTER,
                                        PROGRESS_BAR_STYLE,
                                        SWIGGY_API_CALL_INTERVAL,
                                        SWIGGY_LOGIN_URL, SWIGGY_ORDER_URL,
                                        SWIGGY_SEND_OTP_URL, SWIGGY_URL,
                                        SWIGGY_VERIFY_OTP_URL)
from swiggy_analytics.db import SwiggyDB
from swiggy_analytics.exceptions import (SwiggyAPIError, SwiggyCliAuthError,
                                         SwiggyCliConfigError,
                                         SwiggyCliQuitError, SwiggyDBError)
from swiggy_analytics.queries import (get_items_name_count_query,
                                      get_monthly_spend_count,
                                      get_order_count_day_of_week,
                                      get_top_20_restaurants_query,
                                      get_total_amount_query,
                                      get_total_orders_query)
from swiggy_analytics.utils import (format_amount, get_config, get_month,
                                    get_scores, get_weekday_name, save_config)

session = requests.Session()


def fetch_orders_info(orders):
    """
    Parses the list of orders and extracts only the fields
    required for analytics. Prepares the result as
    input for the db
    """
    order_details = []
    order_items = []
    OrderDetails = namedtuple(
        'OrderDetails', ['order_id', 'order_total', 'restaurant_name', 'order_time', 'rain_mode', 'on_time'])
    OrderItems = namedtuple(
        'OrderItems', ['order_id', 'name', 'is_veg'])

    # filter orders which are delivered
    delivered_orders = list(filter(lambda i: i.get(
        'order_status', '') == 'Delivered', orders))
    for order in delivered_orders:
        order_id = order.get('order_id')
        order_total = order.get('order_total')
        restaurant_name = order.get('restaurant_name')
        order_time = order.get('order_time')
        rain_mode = order.get('rain_mode', False)
        on_time = order.get('on_time', True)

        order_details.append(OrderDetails(order_id=order_id,
                                          order_total=order_total,
                                          restaurant_name=restaurant_name,
                                          order_time=order_time,
                                          rain_mode=rain_mode,
                                          on_time=on_time))
        if order.get('order_items'):
            for item in order.get('order_items'):
                is_veg = item.get('is_veg')
                name = item.get('name')
                order_items.append(OrderItems(order_id=order_id,
                                              name=name,
                                              is_veg=is_veg
                                              ))

    return {'order_details': order_details, 'order_items': order_items}


def fetch_orders(offset_id):
    """
    Fetches a set of orders (limited to 10) using the history API
    """
    try:
        response = session.get(
            SWIGGY_ORDER_URL + '?order_id=' + str(offset_id))
    except requests.exceptions.ConnectionError:
        fetch_orders(offset_id)
    except Exception as e:
        raise SwiggyAPIError("Error while fetching orders: {}".format(e))
    return response.json().get('data').get('orders', [])


def initial_setup_prompt():
    """
    Prompt shown for the first time setup
    or when configure flag is passed.
    Fetch the keys from user and store in config file
    """
    try:
        swiggy_username = get_input_value(title='First time setup',
                                          text='Please enter your mobile number registered with Swiggy')
    except SwiggyCliQuitError:
        sys.exit("Bye")

    save_config(username=swiggy_username)
    return None


def perform_login():
    """
    Attemps to make a GET request to Swiggy and on success,
    uses the CSRF token to make a POST request to login and
    maintain the cookies in the same session object, which is used
    for further calls.
    """
    establish_connection = session.get(SWIGGY_URL)
    # This is the most ugliest parsing I have ever written. Don't @ me
    csrf_token = establish_connection.text.split("csrfToken")[1].split("=")[
        1].split(";")[0][2:-1]
    # Trying to act smart eh, swiggy? ;)
    sw_cookie = establish_connection.cookies.get_dict().get('__SW')
    if not csrf_token or not sw_cookie:
        raise SwiggyCliAuthError("Unable to establish connection with the website. Login failed")
    # fetch username from config
    try:
        username = get_config()
    except SwiggyCliConfigError as e:
        raise e
    # send OTP request

    otp_response = session.post(SWIGGY_SEND_OTP_URL, headers={'content-type': 'application/json',
                                                              'Cookie':'__SW={}'.format(sw_cookie),
                                                              'User-Agent': 'Mozilla/Gecko/Firefox/65.0'
                                                            },
                                  json={"mobile": username, '_csrf': csrf_token})
    # Swiggy APIs send 200 for error responses, so cannot do a status check.
    if otp_response== "Invalid Request":
        raise SwiggyCliAuthError(
            "Error from Swiggy API while sending OTP")
    # prompt for OTP
    otp_input = get_input_value(title='Verify OTP',
                                text='Please enter the OTP sent to your registered mobile number {}'.format(username))

    otp_verify_response = session.post(SWIGGY_VERIFY_OTP_URL, headers={'content-type': 'application/json',
                                                             'User-Agent': 'Mozilla/Gecko/Firefox/65.0'},
                                  json={"otp": otp_input, '_csrf': csrf_token})
    if otp_verify_response.text == "Invalid Request":
        perform_login()

    if otp_verify_response.status_code != 200:
        raise SwiggyCliAuthError(
            "Login response non success {}".format(otp_verify_response.status_code))


def insert_orders_data(db, orders):
    # extract only the fields required for analytics
    try:
        orders_info = fetch_orders_info(orders)
    except SwiggyAPIError as e:
        raise SwiggyAPIError(e)

    # store the order data in db
    try:
        db.insert_orders_details(orders_info.get('order_details'))
    except SwiggyDBError as e:
        print(e)
    try:
        db.insert_order_items(orders_info.get('order_items'))
    except SwiggyDBError as e:
        print(e)


def fetch_and_store_orders(db):
    """
    Fetches all the historical orders for the user and saves them in db
    """
    response = session.get(SWIGGY_ORDER_URL)
    if not response.json().get('data', None):
        raise SwiggyAPIError("Unable to fetch orders")

    # get the last order_id to use as offset param for next order fetch call
    orders = response.json().get('data').get('orders', None)
    # check if user has zero orders
    if isinstance(orders, list) and len(orders)==0:
        sys.exit("You have not placed any order, no data to fetch :)")
    if not orders:
        raise SwiggyAPIError("Unable to fetch orders")

    # extract order meta data and insert in db
    insert_orders_data(db, orders)

    offset_id = orders[-1]['order_id']
    count = response.json().get('data')['total_orders']
    pages = ceil(count/10)
    label = "Fetching {} orders".format(count)

    # Updates the progress bar on every orders fetch call (i.e. after 10 unique orders)
    with ProgressBar(style=PROGRESS_BAR_STYLE, formatters=PROGRESS_BAR_FORMATTER) as pb:
        for i in pb(range(pages), label=label):
            try:
                orders = fetch_orders(offset_id)
            except SwiggyAPIError as e:
                raise SwiggyAPIError(e)
            if len(orders) == 0:
                break

            # extract order meta data and insert in db
            insert_orders_data(db, orders)
            # Responsible Scraping. Code word for "dont wanna overload their servers :P" :)

            time.sleep(SWIGGY_API_CALL_INTERVAL)
            # SAD PANDA FACE BEGIN
            # The way it works is that, the first API call returns a paginated set of 10 orders and to fetch the next result, you need
            # to send the last order_id from this result set as an offset parameter. Because the way this offset/cursor
            # is designed it makes it impossible to use any kind of async/await magic.
            # SAD PANDA FACE OVER
            offset_id = orders[-1]['order_id']


def display_stats(db):
    """
    Queries the DB to get basic stats and display
    using `print_bars`
    """
    print_formatted_text(
        HTML("Some basic stats based on your order history:"))
    # orders summary sec
    try:
        orders_count = db.fetch_result(query=get_total_orders_query)[0][0]
    except SwiggyDBError as e:
        raise("Error while fetching total orders count {}".format(e))
    print_formatted_text(HTML(
        '\nYour total <b>delivered</b> orders are: <skyblue>{}</skyblue>\n'.format(orders_count)))

    try:
        total_amount = db.fetch_result(query=get_total_amount_query)[0][0]
    except SwiggyDBError as e:
        raise("Error while fetching total amount {}".format(e))
    print_formatted_text(HTML(
        'You have spent a total sum of <skyblue>{}</skyblue>'.format(format_amount(total_amount))))

    # spend pattern
    print_formatted_text(
        HTML('\nYour spend and orders count distributed monthly:'))
    try:
        items_count_bar_graph = db.fetch_result(
            query=get_monthly_spend_count)
    except SwiggyDBError as e:
        raise("Error while fetching items v/s count {}".format(e))
    print_bars(get_scores([{"name": get_month(i[0]), "count":i[2], "extra":format_amount(i[1])}
                           for i in items_count_bar_graph]))

    # topK weekdays
    print_formatted_text(HTML(
        '\nWeekday wise distribution of your orders:'))
    try:
        weekday_count_bar_graph = db.fetch_result(
            query=get_order_count_day_of_week)
    except SwiggyDBError as e:
        raise("Error while fetching total orders v/s weekday data {}".format(e))

    print_bars(get_scores([{"name": get_weekday_name(i[0]), "count":i[1]}
                           for i in weekday_count_bar_graph]))

    # topK restaraunts
    print_formatted_text(
        HTML('\nTop <b>10</b> restaraunts from where you have ordered:'))
    try:
        items_count_bar_graph = db.fetch_result(
            query=get_top_20_restaurants_query)
    except SwiggyDBError as e:
        raise("Error while fetching items v/s count {}".format(e))
    print_bars(get_scores([{"name": i[0], "count":i[1]}
                           for i in items_count_bar_graph]))
    # topK items
    print_formatted_text(
        HTML('\nTop <b>10</b> items that you have ordered:'))
    try:
        items_count_bar_graph = db.fetch_result(
            query=get_items_name_count_query)
    except SwiggyDBError as e:
        raise("Error while fetching items v/s count {}".format(e))
    print_bars(get_scores([{"name": i[0], "count":i[1]}
                           for i in items_count_bar_graph]))
