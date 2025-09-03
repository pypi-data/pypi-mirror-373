from django.conf import (
    settings,
)


# Абсолютный путь до директории хранения логов
# ruff: noqa: S108
LOG_PATH = getattr(settings, 'LOG_PATH', '/tmp')
# Включение логирования SQL-запросов
SQL_LOG = getattr(settings, 'SQL_LOG', False)
# Логирование SQL-запросов только зарегистрированных экшенов, функций при помощи декоратора
# m3_db_utils.decorators.log_query
SQL_LOG_ONLY_REGISTERED = getattr(settings, 'SQL_LOG_ONLY_REGISTERED', False)
# Включение дополнительного вывода трейса с местом отправки запроса
SQL_LOG_WITH_STACK_TRACE = getattr(settings, 'SQL_LOG_WITH_STACK_TRACE', False)
# Запрос форматируется со значением полей
SQL_LOG_WITH_PARAMETERS = getattr(settings, 'SQL_LOG_WITH_PARAMETERS', False)
# Максимальная длина запроса для обработки
SQL_LOG_MAX_SIZE = getattr(settings, 'SQL_LOG_MAX_SIZE', 25_000)
# Включает форматирование выводимых SQL-запросов
SQL_LOG_REINDENT = getattr(settings, 'SQL_LOG_REINDENT', False)


if SQL_LOG:
    from django.db.backends import (
        utils as backutils,
    )

    from m3_db_utils.wrappers import (
        DBUtilsCursorDebugWrapper,
    )

    backutils.CursorDebugWrapper = DBUtilsCursorDebugWrapper
    backutils.CursorWrapper = DBUtilsCursorDebugWrapper
