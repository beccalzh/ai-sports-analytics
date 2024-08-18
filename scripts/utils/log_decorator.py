import logging
from functools import wraps
from datetime import datetime
from pprint import pformat
import os
from dotenv import load_dotenv
load_dotenv()

# create log directory
log_dir = os.getenv('LOG_DIR')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# create file name
today = datetime.today().strftime('%Y-%m-%d')
log_filename = os.path.join(log_dir, f'{today}.log')

# set logging
logging.basicConfig(filename=log_filename, 
                    level=logging.ERROR, 
                    format='[%(asctime)s] %(message)s',)

logger = logging.getLogger(__name__)
logger.error(f"Start Time: {datetime.now()}")

def log_decorator(func):
    """decorator for logging function calls and errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logging.info(f"Function {func.__name__} started at {start_time}")
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            logging.error(f"Arguments: {pformat(args)}")
            raise  # raise error for debugging
    return wrapper