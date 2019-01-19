import sys
from exceptions import SwiggyCliQuitError

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import button_dialog, input_dialog
from prompt_toolkit.validation import Validator, ValidationError
from constants import YES_ANSWER_CHOICES, NO_ANSWER_CHOICES


class YesNoValidator(Validator):

    def validate(self, document):
        """
        Display error message if text not valid.

        return:
            A status bar with validation error message
        """
        text = document.text.lower()
        if text not in YES_ANSWER_CHOICES+NO_ANSWER_CHOICES:
            raise ValidationError(message='Enter "yes" if you want to continue '
                                          '"no" if you want to abort.')


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


def user_continue():
    html_completer = WordCompleter(YES_ANSWER_CHOICES+NO_ANSWER_CHOICES)
    answer = prompt('Enter HTML: ', completer=html_completer,
                    validator=YesNoValidator())

    if answer in YES_ANSWER_CHOICES:
        return True
    return False
