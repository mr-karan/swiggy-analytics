from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import input_dialog
from exceptions import SwiggyCliQuitError


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


def get_input_value(title, text):
    '''
    Handle input by user
    '''
    value = input_dialog(title, text)
    if not value:
        # if user decides to cancel
        if not quit_prompt():
            # show the input dialogue again if user doesn't want to quit
            return input_dialog(title, text)
        # in case user wants to cancel
        raise SwiggyCliQuitError("No input provided by user")
    # raw value entered by user
    return value
