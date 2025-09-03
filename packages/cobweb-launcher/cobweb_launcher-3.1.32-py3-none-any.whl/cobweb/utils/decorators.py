import time
from functools import wraps
from cobweb.base import logger


def decorator_oss_db(exception, retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(callback_func, *args, **kwargs):
            result = None
            for i in range(retries):
                msg = None
                try:
                    return func(callback_func, *args, **kwargs)
                except Exception as e:
                    result = None
                    msg = e
                finally:
                    if result:
                        return result

                    if i >= 2 and msg:
                        raise exception(msg)

        return wrapper

    return decorator


def check_pause(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        while not self.pause.is_set():
            try:
                func(self, *args, **kwargs)
            except Exception as e:
                logger.info(f"{func.__name__}: " + str(e))
            finally:
                time.sleep(0.1)
        logger.info(f"Pause detected: {func.__name__} thread closing...")

    return wrapper
