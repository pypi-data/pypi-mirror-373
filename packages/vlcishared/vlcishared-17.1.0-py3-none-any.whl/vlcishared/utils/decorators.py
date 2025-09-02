import logging
import time
from functools import wraps


def log_timer(func):
    '''Logea el tiempo que tarda en ejecutarse una función'''

    @wraps(func)
    def log_func(*args, **kwargs):
        start_time = time.time()
        result = func(*args)
        exc_time = time.time() - start_time
        log = logging.getLogger()
        log.info("La función {} se ejecuto en {} segundos".format(
            func.__name__, exc_time))

        return result
    return log_func
