from functools import wraps
from google.api_core.exceptions import NotFound
import time

MAX_NUMBER_OF_ATTEMPTS = 2


def retry_on_not_found(wrapped_function):
    """This decorator retry call when table is not found. Insert into newly created table often fails with error
    because API probably needs few seconds to see new created table"""

    @wraps(wrapped_function)
    def inner(*args, **kwargs):
        for i in range(1, MAX_NUMBER_OF_ATTEMPTS + 1):
            try:
                kwargs["attempts"] = i
                return wrapped_function(*args, **kwargs)
                # this is because all request share same service
            except NotFound as err:
                time.sleep(2)

    return inner
