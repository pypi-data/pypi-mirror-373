import timeit

from ms_utils.logging_lib import Logger

logger = Logger.setup_logger(__name__)
logger.propagate = False


def time_it_decorator(func):
    """Timeit decorator to measure execution time of a function."""

    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        logger.info(
            f"{func.__name__} executed in {end_time - start_time:.8f}s"
        )
        return result

    return wrapper
