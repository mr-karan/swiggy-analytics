from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import input_dialog
from exceptions import SwiggyCliQuitError
import sys


def quit_prompt():
    '''
    Generic function to display a confirmation screen shown if
    user decides to cancel any operation.
    '''
    result = button_dialog(
        title='Are you sure you want to exit?',
        text='Do you want to confirm?',
        buttons=[
            ('Yes', True),
            ('No', False),
        ],
    )
    return result


def get_input_value(title, text, password=False):
    '''
    Handle input by user
    '''
    value = input_dialog(title, text, password=password)
    if not value:
        # if user decides to cancel
        if not quit_prompt():
            # show the input dialogue again if user doesn't want to quit
            return input_dialog(title, text, password=password)
        # in case user wants to cancel
        raise SwiggyCliQuitError("No input provided by user")
    # raw value entered by user
    return value


def print_bars(items=None, block=u"\u2580", width=50):
    """Print unicode bar representations of dates and scores."""
    items = [{'count': 20, 'weekend': True, 'score': 0.4},
             {'count': 40, 'weekend': False, 'score': 0.6}]
    for i in range(len(items)):
        num = str(items[i]["count"])

        sys.stdout.write("hey")
        sys.stdout.write("  ")
        sys.stdout.write(num)
        sys.stdout.write((5 - len(num)) * " ")

        # Colour the weekend bars.
        if items[i]["weekend"]:
            sys.stdout.write("\033[93m")

        sys.stdout.write(block * int(items[i]["score"] * width))

        if items[i]["weekend"]:
            sys.stdout.write("\x1b[0m")

        sys.stdout.write("\n")
