import logging
import time

from contextlib import contextmanager
from functools import wraps


logger = logging.getLogger(__name__)

def log_execution_time(func):
    """Decorator that logs the execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        logger.info(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result
    return wrapper

def log_block_time(block_name: str):
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"\t[{block_name}] Execution time: {elapsed_time:.4f} seconds")
