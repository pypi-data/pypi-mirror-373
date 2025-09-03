import logging.handlers

from m3_db_utils.settings import (
    SQL_LOG_MAX_SIZE,
    SQL_LOG_REINDENT,
)


class ConsoleSQLFormatter(logging.Formatter):
    """Форматер для логирования SQL-запросов в консоль."""

    def format(self, record):
        """Форматирует запись лога."""
        # Проверка на доступность Pygments для раскраски кода
        try:
            import pygments
            from pygments.formatters import (
                TerminalTrueColorFormatter,
            )
            from pygments.lexers import (
                SqlLexer,
            )
        except ImportError:
            pygments = None

        # Проверка на доступность sqlparse для форматирования
        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        sql = record.sql.strip()

        database = getattr(record, 'database', 'default')

        if len(sql) < SQL_LOG_MAX_SIZE:
            if sqlparse:
                # Форматирование кода
                sql = sqlparse.format(
                    sql=sql,
                    reindent=SQL_LOG_REINDENT,
                    strip_comments=True,
                )

            if pygments:
                # Раскраска sql-запроса
                sql = pygments.highlight(
                    sql,
                    SqlLexer(),
                    TerminalTrueColorFormatter(
                        style='friendly',
                    ),
                )

        stack_trace = getattr(record, 'stack_trace', None)
        stack_trace = f'\n{stack_trace}\n' if stack_trace else ''

        db_prefix = f'[DB: {database}] '
        record.statement = f'\n{db_prefix}{sql}{stack_trace}' if SQL_LOG_REINDENT else f'{db_prefix}{sql}{stack_trace}'

        return super().format(record)


class FileSQLFormatter(logging.Formatter):
    """Форматер для логирования SQL-запросов в файл."""

    def format(self, record):
        """Форматирует запись лога."""
        database = getattr(record, 'database', 'default')

        sql = record.sql.strip()

        stack_trace = getattr(record, 'stack_trace', None)
        stack_trace = f'\n{stack_trace}\n' if stack_trace else ''

        db_prefix = f'[DB: {database}] '
        record.statement = f'{db_prefix}{sql}{stack_trace}'

        return super().format(record)
