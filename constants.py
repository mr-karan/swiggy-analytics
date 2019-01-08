import os
from pathlib import Path


SWIGGY_URL = 'https://www.swiggy.com'
SWIGGY_LOGIN_URL = SWIGGY_URL + '/dapi/auth/signin-with-check'
SWIGGY_ORDER_URL = SWIGGY_URL + '/dapi/order/all'

CONFIG_FILEPATH = os.path.join(str(Path.home()), '.swiggy-expense-config.ini')
