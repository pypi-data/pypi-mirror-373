import threading
from functools import (
    wraps,
)


def log_query(log_query_name):
    """Декоратор на экшен.

    Под наименованием log_query_name логирует стэктрейс всех мест в экшене, которые создают и отправляют запросы в БД.
    """

    def inner(action):
        @wraps(action)
        def wrapper(self, request, context, *args, **kwargs):
            thread_locals = threading.local()

            setattr(thread_locals, 'log_query', log_query_name)

            try:
                result = action(self, request, context, *args, **kwargs)

            finally:
                delattr(thread_locals, 'log_query')

            return result

        return wrapper

    return inner
