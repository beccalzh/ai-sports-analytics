import logging
import functools
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# create log directory
log_dir = os.getenv('LOG_DIR')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# create file name
today = datetime.today().strftime('%m%d')
log_filename = os.path.join(log_dir, f'{today}.log')

# set logging
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='[%(asctime)s] %(levelname)s: %(message)s')

def log_decorator(func):
    """decorator for logging function calls and errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logging.info(f"Function {func.__name__} started at {start_time}")
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            logging.info(f"Function {func.__name__} ended at {end_time}")
            logging.info(f"Function {func.__name__} executed in {end_time - start_time}")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            logging.error(f"Arguments: {args}, {kwargs}")
            raise  # raise error for debugging
    return wrapper