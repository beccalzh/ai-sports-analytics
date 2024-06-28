import logging
import functools
from datetime import datetime
import os

# create log directory
log_dir = '../log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# create file name
today = datetime.today().strftime('%m%d')
script_name = os.path.splitext(os.path.basename(__file__))[0]
log_filename = os.path.join(log_dir, f'{script_name}_{today}.log')

# set logging
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')

def log_decorator(func):
    """decorator for logging function calls and errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(f"Called {func.__name__} with args={args} kwargs={kwargs}")
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise  # raise error for debugging
    return wrapper