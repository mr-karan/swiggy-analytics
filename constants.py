import os
from pathlib import Path

from prompt_toolkit.shortcuts.progress_bar import formatters
from prompt_toolkit.styles import Style

SWIGGY_URL = 'https://www.swiggy.com'
SWIGGY_LOGIN_URL = SWIGGY_URL + '/dapi/auth/signin-with-check'
SWIGGY_ORDER_URL = SWIGGY_URL + '/dapi/order/all'

CONFIG_FILEPATH = os.path.join(str(Path.home()), '.swiggy-expense-config.ini')

PROGRESS_BAR_STYLE = Style.from_dict({
    'label': 'bg:#FFA500 #000000',
    'percentage': 'bg:#FFA500 #000000',
    'current': '#448844',
    'bar': '',
})

PROGRESS_BAR_FORMATTER = [
    formatters.Label(),
    formatters.Text(': [', style='class:percentage'),
    formatters.Percentage(),
    formatters.Text(']', style='class:percentage'),
    formatters.Text(' '),
    formatters.Bar(sym_a='#', sym_b='#', sym_c='.'),
    formatters.Text('  '),
]
