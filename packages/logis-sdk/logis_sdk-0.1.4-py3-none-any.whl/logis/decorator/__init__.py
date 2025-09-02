import logging
import time
from functools import wraps


def log_execution_time(func):
    """
    打印执行事件
    TODO：考虑生成器方法
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.debug(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper
